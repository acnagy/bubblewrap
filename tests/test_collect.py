import pytest
import os

import collect


def test__extract_module_name():
    test = "/path/to/code/bubblewrap/tests/test_collect.py"
    expected = "test_collect"
    assert collect._extract_module_name(test) == expected


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


def test_examples_stable():
    expected = {
        "banana": [
            "/path/to/code/bubblewrap/examples/stable/tests/test_banana.py",
            "/path/to/code/bubblewrap/examples/stable/tests/test_amazing.py",
        ],
        "amazing": [
            "/path/to/code/bubblewrap/examples/stable/tests/test_banana.py",
            "/path/to/code/bubblewrap/examples/stable/tests/test_amazing.py",
            "/path/to/code/bubblewrap/examples/stable/tests/test_apple.py",
        ],
        "blue": [
            "/path/to/code/bubblewrap/examples/stable/tests/test_banana.py",
            "/path/to/code/bubblewrap/examples/stable/tests/test_apple.py",
        ],
        "script": [
            "/path/to/code/bubblewrap/examples/stable/tests/test_script.py",
            "/path/to/code/bubblewrap/examples/stable/tests/test_apple.py",
        ],
        "apple": ["/path/to/code/bubblewrap/examples/stable/tests/test_apple.py"],
    }
    test_location = os.path.join(os.path.abspath("."), "examples", "stable")
    # order doesn't matter, so the test sorts so we're only checking if we have the same stuff
    # in the output as expected
    assert sorted(collect.collect_tests(test_location, exclude=[])) == sorted(expected)


def test__add_test_to_map():
    root = os.getcwd()
    example_stable = os.path.join(root, "examples", "stable")

    test_path = f"{root}/examples/stable/tests/test_banana.py"

    exclude = [".git", "__pycache__", "__venv__", "env"]
    all_files = collect.walk_tree(example_stable, exclude)
    tests = collect.filter_tests(all_files)
    modules = collect.convert_app_paths_to_modules(set(all_files) - set(tests))

    output = collect._add_test_to_map(test_path, modules, {})
    expected = {
        "banana": [
            f"{root}/examples/stable/tests/test_banana.py",
        ],
        "blue": [
            f"{root}/examples/stable/tests/test_banana.py",
        ],
        "amazing": [
            f"{root}/examples/stable/tests/test_banana.py",
        ],
    }

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
    output = collect.collect_tests(example_stable, exclude)
    assert output == expected
