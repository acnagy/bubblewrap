"""
Functionality to walk a package's tree in search of Python files, filter module imports for which main
modules test modules are operating on, and return a map of modules to tests that assess them
"""

import os
import ast
import logging

from typing import Dict, List, Set

logger = logging.getLogger(__name__)


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

    return map_imports(tests, app_modules)


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
        module = _extract_module_name(file)
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
        module = _extract_module_name(fullpaths.pop())
        app_modules.add(module)

    return app_modules


def map_imports(tests: List[str], app_modules: Set[str]):
    """
    identifies the modules that the test files cover, and maps the tests to the
    modules that they cover
    """
    modules_map = {}
    for test in tests:
        modules_map = _add_test_to_map(test, app_modules, modules_map)

    return modules_map


def _add_test_to_map(
    test_path: str, app_modules: Set[str], module_map: Dict
) -> Dict[str, List[str]]:
    """
    walks the abstract syntax tree for a python module (opened from it's fullpath) and
    identifies all of the modules that it imports
    """
    syntax_tree = ast.parse(open(test_path).read())
    imports = []
    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            imports += [child.name for child in node.names]
        # an import from could be in the form of:
        # from directory import module
        # OR
        # from module import member
        # so to be sure we don't miss anything, we add the node.module ("from module ..")
        # we'll filter things that are NOT actual modules in the package tree later
        if isinstance(node, ast.ImportFrom):
            imports.append(node.module)

    # filter out stdlib and invalid imports - anything that is both an import and a module
    # in this application is something we care about
    imports = set(imports).intersection(app_modules)
    for app_module in imports:
        if app_module in module_map:
            module_map[app_module].append(test_path)
        else:
            module_map[app_module] = [test_path]
    return module_map


def _extract_module_name(fullpath: str) -> str:
    module = fullpath.split(os.path.sep)
    # strip off .py extension to get module name
    return module[len(module) - 1][:-3]
