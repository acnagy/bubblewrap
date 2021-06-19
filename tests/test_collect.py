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


def test_examples_one():
    expected = {
        "banana": [
            "/path/to/code/bubblewrap/examples/one/tests/test_banana.py",
            "/path/to/code/bubblewrap/examples/one/tests/test_amazing.py",
        ],
        "amazing": [
            "/path/to/code/bubblewrap/examples/one/tests/test_banana.py",
            "/path/to/code/bubblewrap/examples/one/tests/test_amazing.py",
            "/path/to/code/bubblewrap/examples/one/tests/test_apple.py",
        ],
        "blue": [
            "/path/to/code/bubblewrap/examples/one/tests/test_banana.py",
            "/path/to/code/bubblewrap/examples/one/tests/test_apple.py",
        ],
        "script": [
            "/path/to/code/bubblewrap/examples/one/tests/test_script.py",
            "/path/to/code/bubblewrap/examples/one/tests/test_apple.py",
        ],
        "apple": ["/path/to/code/bubblewrap/examples/one/tests/test_apple.py"],
    }
    test_location = os.path.join(os.path.abspath("."), "examples", "one")
    # order doesn't matter, so the test sorts so we're only checking if we have the same stuff
    # in the output as expected
    assert sorted(collect.collect_tests(test_location, exclude=[])) == sorted(expected)
