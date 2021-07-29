import pytest
import os
import dataclasses

import run

from random import randint

from collect import collect_tests


@pytest.fixture
def paths():
    root = os.getcwd()
    example_stable = os.path.join(root, "examples", "stable")
    test_path = f"{root}/examples/stable/tests/test_amazing.py"
    return example_stable, test_path


def test_Test_run(paths):
    project_path, test_path = paths
    output = run.Test(project_path=project_path, test_path=test_path, trials=1)
    output.run()
    expected = run.Test()
    expected.project_path = project_path
    expected.test_path = test_path
    expected.trials = 1
    expected.runtime_sum = output.runtime_sum  # values don't so just allowing everythin
    expected.avg_runtime = output.avg_runtime
    expected.passes = 1
    expected.pass_rate = 1.0
    expected.fails = 0
    expected.fail_rate = 0
    expected.flakes = 0
    expected.flake_rate = 0
    expected.passed = True

    assert output == expected
    assert output.runtime_sum > 0
    assert output.avg_runtime > 0


def test_Cache(paths):
    project_path, test_path = paths
    entry = run.Test(project_path=project_path, test_path=test_path, trials=1)
    results = run.Results(tests={})
    results.put(test_path, entry)
    assert results.get(test_path) == entry


def test_run_tests(paths):
    project_path, test_path = paths
    collected = collect_tests(project_path, [".git", "__pycache__", "__venv__", "env"])
    module_list = run.run_tests(project_path, 1, collected)

    assert isinstance(module_list, dict)
    assert len(module_list.get("tests")) == 4
