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
    expected.latency_sum = output.latency_sum  # values don't so just allowing everythin
    expected.avg_latency = output.avg_latency
    expected.passes = 1
    expected.pass_rate = 1.0
    expected.fails = 0
    expected.fail_rate = 0
    expected.flakes = 0
    expected.flake_rate = 0
    expected.passed = True

    assert output == expected
    assert output.latency_sum > 0
    assert output.avg_latency > 0


def test_Module_summarize(paths, module_name):
    project_path, test_path = paths
    test = run.Test(project_path=project_path, test_path=test_path, trials=1)
    test.run()
    output = run.Module(name=module_name, test_results=[test])
    output.summarize()
    expected = run.Module(name=module_name, test_results=[test])
    expected.flake_rate = 0
    expected.latency = output.latency  # this doesn't matter, so setting as the same
    assert output == expected
    assert output.latency > 0


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

    assert isinstance(module_list, list)
    assert len(module_list) == 5

    module = module_list.pop()
    assert isinstance(module, run.Module)
    assert isinstance(module.name, str)
    assert isinstance(module.test_results, list)

    test_result = module.test_results.pop()
    assert isinstance(test_result, run.Test)
    assert test_result.project_path == project_path


def test_find_flakiest_tests():
    module_one = run.Module(name="one", test_results=[])
    module_one.flake_rate = 0.1
    module_two = run.Module(name="two", test_results=[])
    module_two.flake_rate = 0.2
    module_three = run.Module(name="three", test_results=[])
    module_three.flake_rate = 0.6
    module_four = run.Module(name="four", test_results=[])
    module_four.flake_rate = 0.4
    module_five = run.Module(name="five", test_results=[])
    module_five.flake_rate = 0.3

    # test a bunch of even-numbered permutations
    input_list = [module_three, module_one, module_two, module_four]
    output_rate, output_modules = run.find_flakiest_tests(input_list)
    assert output_rate == 0.6
    assert output_modules == [dataclasses.asdict(module_three)]

    input_list = [module_two, module_three, module_one, module_four]
    output_rate, output_modules = run.find_flakiest_tests(input_list)
    assert output_rate == 0.6
    assert output_modules == [dataclasses.asdict(module_three)]

    input_list = [module_two, module_four, module_three, module_one]
    output_rate, output_modules = run.find_flakiest_tests(input_list)
    assert output_rate == 0.6
    assert output_modules == [dataclasses.asdict(module_three)]

    input_list = [module_two, module_one, module_four, module_three]
    output_rate, output_modules = run.find_flakiest_tests(input_list)
    assert output_rate == 0.6
    assert output_modules == [dataclasses.asdict(module_three)]

    # test a bunch of odd-numbered permutations
    input_list = [module_three, module_five, module_one, module_two, module_four]
    output_rate, output_modules = run.find_flakiest_tests(input_list)
    assert output_rate == 0.6
    assert output_modules == [dataclasses.asdict(module_three)]

    input_list = [module_two, module_five, module_three, module_one, module_four]
    output_rate, output_modules = run.find_flakiest_tests(input_list)
    assert output_rate == 0.6
    assert output_modules == [dataclasses.asdict(module_three)]

    input_list = [module_two, module_four, module_three, module_five, module_one]
    output_rate, output_modules = run.find_flakiest_tests(input_list)
    assert output_rate == 0.6
    assert output_modules == [dataclasses.asdict(module_three)]

    input_list = [module_two, module_one, module_five, module_four, module_three]
    output_rate, output_modules = run.find_flakiest_tests(input_list)
    assert output_rate == 0.6
    assert output_modules == [dataclasses.asdict(module_three)]


def test_find_flakiest_tests_empty():
    output_rate, output_modules = run.find_flakiest_tests([])
    assert output_rate == None
    assert output_modules == []


def test_find_flakiest_tests_one_entry():
    module = run.Module(name="one", test_results=[])
    module.flake_rate = 0.5
    output_rate, output_modules = run.find_flakiest_tests([module])
    assert output_rate == 0.5
    assert output_modules == [dataclasses.asdict(module)]


def test_find_flakiest_tests_all_zeros():
    module_one = run.Module(name="one", test_results=[])
    module_one.flake_rate = 0
    module_two = run.Module(name="two", test_results=[])
    module_two.flake_rate = 0
    module_three = run.Module(name="three", test_results=[])
    module_three.flake_rate = 0
    module_four = run.Module(name="four", test_results=[])
    module_four.flake_rate = 0

    input_list = [module_three, module_one, module_two, module_four]
    output_rate, output_modules = run.find_flakiest_tests(input_list)
    assert output_rate == 0

    expected_modules = [
        dataclasses.asdict(module_three),
        dataclasses.asdict(module_one),
        dataclasses.asdict(module_two),
        dataclasses.asdict(module_four),
    ]
    assert output_modules == expected_modules


def test_find_flakiest_tests_duplicate():
    module_one = run.Module(name="one", test_results=[])
    module_one.flake_rate = 0.1
    module_two = run.Module(name="two", test_results=[])
    module_two.flake_rate = 0.4
    module_three = run.Module(name="three", test_results=[])
    module_three.flake_rate = 0.6
    module_four = run.Module(name="four", test_results=[])
    module_four.flake_rate = 0.4
    module_five = run.Module(name="five", test_results=[])
    module_five.flake_rate = 0.3

    input_list = [module_three, module_one, module_two, module_four, module_five]
    output_rate, output_modules = run.find_flakiest_tests(input_list)
    assert output_rate == 0.6
    assert output_modules == [dataclasses.asdict(module_three)]


def test_find_make_flake_rate_duplicate_max():
    module_one = run.Module(name="one", test_results=[])
    module_one.flake_rate = 0.1
    module_two = run.Module(name="two", test_results=[])
    module_two.flake_rate = 0.6
    module_three = run.Module(name="three", test_results=[])
    module_three.flake_rate = 0.6
    module_four = run.Module(name="four", test_results=[])
    module_four.flake_rate = 0.4
    module_five = run.Module(name="five", test_results=[])
    module_five.flake_rate = 0.3

    input_list = [module_three, module_one, module_two, module_four, module_five]
    output_rate, output_modules = run.find_flakiest_tests(input_list)
    assert output_rate == 0.6
    assert output_modules == [dataclasses.asdict(module_three), dataclasses.asdict(module_two)]


def test_find_flakiest_tests_super_long():
    input_list = []
    for i in range(0, 10000):
        module = run.Module(name="looong", test_results=[])
        module.flake_rate = randint(1, 1000) // 1001
        input_list.append(module)

    winner = run.Module(name="winner", test_results=[])
    winner.flake_rate = 10
    input_list.insert(randint(2, 999), winner)

    output_rate, output_modules = run.find_flakiest_tests(input_list)
    assert output_rate == winner.flake_rate
    assert len(output_modules) == 1

    output_module = output_modules.pop()
    assert output_module["name"] == "winner"
