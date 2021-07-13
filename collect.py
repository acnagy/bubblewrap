"""
Functionality to walk a package's tree in search of Python files, filter module imports for which main
modules test modules are operating on, and return a map of modules to tests that assess them
"""

import os
import ast
import logging
import multiprocessing

from typing import Dict, List, Set
from multiprocessing import Pool, cpu_count
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ImportParser:
    tests: None
    app_modules: None
    module_map: None

    def run(self):
        pool = Pool(processes=cpu_count() // 2)
        for test in self.tests:
            pool.apply_async(self._find_imports, args=(test,), callback=self._add_imports_to_map)
        pool.close()
        pool.join()
        return self.module_map

    def _find_imports(self, test_path: str):
        """
        walks the abstract syntax tree for a python module (opened from it's fullpath) and
        identifies all of the modules that it imports
        """
        syntax_tree = ast.parse(open(test_path).read())
        imports = []
        for node in ast.walk(syntax_tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                imports += [self._submodule_name(child.name) for child in node.names]
            # an import from could be in the form of:
            # from directory import module
            # OR
            # from module import member
            # so to be sure we don't miss anything, we add the node.module ("from module ..")
            # we'll filter things that are NOT actual modules in the package tree later
            if isinstance(node, ast.ImportFrom):
                imports.append(self._submodule_name(node.module))

        imports = set(imports).intersection(self.app_modules)
        return (imports, test_path)

    def _add_imports_to_map(self, found_imports: (Set, str)):
        imports, test_path = found_imports[0], found_imports[1]
        for module in imports:
            if module in self.module_map:
                self.module_map[module].append(test_path)
            else:
                self.module_map[module] = [test_path]

    def _submodule_name(self, name: str) -> str:
        if "." in name:
            name = name.split(".")
            name = name[len(name) - 1]
        return name


def collect_tests(path: str, exclude: List) -> Dict[str, List[str]]:
    """
    identifies all the .py application and test files in the requested path,
    filters them into two separate groups, then maps the application modules
    to the tests that import (aka cover) them
    """
    logger.info("Walking tree for %s...", path)
    all_files = walk_tree(path, exclude)

    logger.info("Filtering for test files...")
    tests = filter_tests(all_files)

    logger.info("Filtering for application files...")
    # we can use set subtraction here, because we're working with full
    # file paths, which means the file paths must be unique
    app_modules_fullpath = set(all_files) - set(tests)

    logger.info("Mapping tests to the application files they cover...")
    app_modules = convert_app_paths_to_modules(app_modules_fullpath)

    parser = ImportParser(tests=tests, app_modules=app_modules, module_map={})
    return parser.run()


def walk_tree(path: str, exclude: List) -> List[str]:
    """
    identify the full paths of all the .py files contained in the path requested,
    ignoring any files contained within the list of exclusions
    """
    exclude = set(exclude)  # exclude sources data from user input, so there could be dups
    python_files = []
    # https://github.com/python/cpython/blob/3.8/Lib/os.py#L280
    for dirpath, dirnames, filenames in os.walk(path, topdown=True):
        dirnames[:] = [dirname for dirname in dirnames if dirname not in exclude]
        for f in filenames:
            if f.endswith(".py"):
                python_files.append(os.path.join(dirpath, f))
    return python_files


def filter_tests(files: List[str]) -> List[str]:
    """
    checks for whether the full filepaths we have are actual python files and
    include the pytest required test_ prefix or _test suffix
    """
    tests = []
    for file in files:
        module = _module_name_from_path(file)
        if module.startswith("test_") or module.endswith("_test"):
            tests.append(file)
    return tests


def convert_app_paths_to_modules(fullpaths: List[str]) -> Set[str]:
    """
    convert full filepath for app files to just the module name, so we can
    finally map modules to the tests that cover them
    """
    app_modules = set()
    while fullpaths:
        module = _module_name_from_path(fullpaths.pop())
        app_modules.add(module)

    return app_modules


def _module_name_from_path(fullpath: str) -> str:
    module = fullpath.split(os.path.sep)
    # strip off .py extension to get module name
    return module[len(module) - 1][:-3]
