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


@pytest.fixture
def module_name():
    return "amazing"


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


def test_Module_summarize(paths, module_name):
    project_path, test_path = paths
    test = run.Test(project_path=project_path, test_path=test_path, trials=1)
    test.run()
    output = run.Module(name=module_name, test_results=[test])
    output.summarize()
    expected = run.Module(name=module_name, test_results=[test])
    expected.flake_rate = 0
    expected.runtime = output.runtime  # this doesn't matter, so setting as the same
    assert output == expected
    assert output.runtime > 0


def test_Cache(paths):
    project_path, test_path = paths
    entry = run.Test(project_path=project_path, test_path=test_path, trials=1)
    cache = run.Cache(results={})
    cache.put(test_path, entry)
    assert cache.get(test_path) == entry


def test_run_tests(paths):
    project_path, test_path = paths
    collected = collect_tests(project_path, [".git", "__pycache__", "__venv__", "env"])
    module_list = run.run_tests(project_path, 1, collected)

    assert isinstance(module_list.modules, list)
    assert len(module_list.modules) == 5

    module = module_list.modules.pop()
    assert isinstance(module, run.Module)
    assert isinstance(module.name, str)
    assert isinstance(module.test_results, list)

    test_result = module.test_results.pop()
    assert isinstance(test_result, run.Test)
    assert test_result.project_path == project_path
