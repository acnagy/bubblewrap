import pytest
import os


import summarize
import run

from random import randint
from dataclasses import asdict


@pytest.fixture
def paths():
    root = os.getcwd()
    example_stable = os.path.join(root, "examples", "stable")
    test_path = f"{root}/examples/stable/tests/test_amazing.py"
    return example_stable, test_path


@pytest.fixture
def module():
    return {"amazing": ["examples/stable/tests/test_amazing.py"]}


def test_summarize(paths, module):
    project_path, test_path = paths
    module_name = list(module.keys())[0]
    test = run.Test(project_path=project_path, test_path=test_path, trials=1)
    test.run()
    test_results = {"tests": {module[module_name][0]: asdict(test)}}
    output = summarize.summarize_module_test_results(module, test_results)
    expected = summarize.ModuleCollection(
        modules=[
            summarize.Module(
                name="amazing",
                trials=1,
                flakes=0.0,
                total_runtime=21.11,
                flake_rate=0.0,
                runtime=21.11,
            )
        ],
        runtimes=[21.11],
    )

    assert isinstance(output, summarize.ModuleCollection)
    assert (
        str(output.runtimes[0])[:1] == str(expected.runtimes[0])[:1]
    )  # just checking the first sig fig is totally fine
    output = output.modules[0]
    expected = expected.modules[0]
    assert isinstance(output, summarize.Module)

    assert output.name == expected.name
    assert output.trials == expected.trials
    assert output.flakes == expected.flakes
    assert output.flake_rate == expected.flake_rate
    assert str(output.runtime)[:1] == str(expected.runtime)[:1]  # same here


def test_keyify():
    input_vals = ["pig", "porpoise", "parrot", "cow", "buffalo", "lynx"]
    expected = b"\x94\x9er\xa9Wx\xf0\xe9$2\x8d\xfeH\xb6\xda\xb4"
    output = summarize.keyify(input_vals)
    assert isinstance(output, bytes)
    assert output == expected


def test_floor():
    output = summarize.floor(3.1415)
    expected = 3
    assert output == expected

    output = summarize.floor(2.7360)
    expected = 2
    assert output == expected
