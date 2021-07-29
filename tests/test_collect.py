import pytest
import os

import collect


def test__module_name_from_path():
    test = "/path/to/code/bubblewrap/tests/test_collect.py"
    expected = "test_collect"
    assert collect._module_name_from_path(test) == expected


def test_filter_tests():
    trial = [
        "/path/to/code/bubblewrap/collect.py",
        "/path/to/code/bubblewrap/cli.py",
        "/path/to/code/bubblewrap/tests/test_collect.py",
        "/path/to/code/bubblewrap/utils/log.py",
        "/path/to/code/bubblewrap/tests/collect_test.py",
        "/path/to/code/bubblewrap/tests/collect_tests.py",
    ]

    trial = collect.filter_tests(trial)
    expected = [
        "/path/to/code/bubblewrap/tests/collect_test.py",
        "/path/to/code/bubblewrap/tests/test_collect.py",
    ]
    # order doesn't matter so we might as well sort to make the test validate it's
    # at least got the same stuff
    assert sorted(trial) == sorted(expected)


def test_ImportParser_find_imports():
    root = os.getcwd()
    example_stable = os.path.join(root, "examples", "stable")

    test_path = f"{root}/examples/stable/tests/test_banana.py"

    exclude = [".git", "__pycache__", "__venv__", "env"]
    all_files = collect.walk_tree(example_stable, exclude)
    tests = collect.filter_tests(all_files)
    modules = collect.convert_app_paths_to_modules(set(all_files) - set(tests))

    output = collect.ImportParser(tests=tests, app_modules=modules, module_map={})._find_imports(
        test_path
    )
    expected = (
        {"banana", "amazing", "blue"},
        f"{root}/examples/stable/tests/test_banana.py",
    )
    assert output == expected


def test_ImportParser_submodule_name_module():
    output = collect.ImportParser(tests=None, app_modules=None, module_map=None)._submodule_name(
        "lizard"
    )
    expected = "lizard"
    assert output == expected


def test_ImportParser_submodule_name_submodule():
    output = collect.ImportParser(tests=None, app_modules=None, module_map=None)._submodule_name(
        "green.lizard"
    )
    expected = "lizard"
    assert output == expected


def test_ImportParser_submodule_name_subsubmodule():
    output = collect.ImportParser(tests=None, app_modules=None, module_map=None)._submodule_name(
        "super.green.lizard"
    )
    expected = "lizard"
    assert output == expected


def test_example_stable_end_to_end():
    root = os.getcwd()
    example_stable = os.path.join(root, "examples", "stable")
    expected = {
        "banana": [
            f"{root}/examples/stable/tests/test_banana.py",
            f"{root}/examples/stable/tests/test_amazing.py",
        ],
        "blue": [
            f"{root}/examples/stable/tests/test_banana.py",
            f"{root}/examples/stable/tests/test_apple.py",
        ],
        "amazing": [
            f"{root}/examples/stable/tests/test_banana.py",
            f"{root}/examples/stable/tests/test_amazing.py",
            f"{root}/examples/stable/tests/test_apple.py",
        ],
        "script": [
            f"{root}/examples/stable/tests/test_script.py",
            f"{root}/examples/stable/tests/test_apple.py",
        ],
        "apple": [f"{root}/examples/stable/tests/test_apple.py"],
    }
    # lifted from defaults in script invocation wrapper
    exclude = [".git", "__pycache__", "__venv__", "env"]
    tests = collect.collect_tests(example_stable, exclude)
    output = collect.map_tests_to_modules(example_stable, exclude, tests)
    assert sorted(output) == sorted(expected)
