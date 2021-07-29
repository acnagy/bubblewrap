import pytest
import os
import dataclasses

import analyze

from random import randint
from run import Test
from summarize import Module, ModuleCollection


# there are nicer ways of doing this
@pytest.fixture()
def stable_mock():
    root = os.getcwd()
    return ModuleCollection(
        modules=[
            Module(
                name="blue",
                flake_rate=0.0,
                runtime=47.39793066666668,
            ),
            Module(
                name="banana",
                flake_rate=0.0,
                runtime=49.28530566666667,
            ),
            Module(
                name="amazing",
                flake_rate=0.0,
                runtime=69.96991666666667,
            ),
            Module(
                name="script",
                flake_rate=0.0,
                runtime=41.20209666666671,
            ),
            Module(
                name="apple",
                flake_rate=0.0,
                runtime=20.684611000000002,
            ),
        ],
        runtimes=[47, 49, 69, 41, 20],
    )


@pytest.fixture
def flake_mock():
    root = os.getcwd()
    return ModuleCollection(
        modules=[
            Module(
                name="alligator",
                flake_rate=0.0,
                runtime=33.639694333333324,
            ),
            Module(
                name="awesome",
                flake_rate=0.6666666666666666,
                runtime=55.760194333333325,
            ),
        ],
        runtimes=[0.03, 0.06],
    )


@pytest.fixture
def stable_test_results_mock():
    return {
        "tests": {
            "examples/stable/tests/test_banana.py": {
                "project_path": "examples/stable",
                "test_path": "examples/stable/tests/test_banana.py",
                "trials": 3,
                "runtime_sum": 26.446166999999967,
                "avg_runtime": 8.815388999999989,
                "passes": 0,
                "pass_rate": 0.0,
                "fails": 3,
                "fail_rate": 1.0,
                "flakes": 0,
                "flake_rate": 0.0,
                "passed": False,
            },
            "examples/stable/tests/test_amazing.py": {
                "project_path": "examples/stable",
                "test_path": "examples/stable/tests/test_amazing.py",
                "trials": 3,
                "runtime_sum": 10.20462400000005,
                "avg_runtime": 3.40154133333335,
                "passes": 0,
                "pass_rate": 0.0,
                "fails": 3,
                "fail_rate": 1.0,
                "flakes": 0,
                "flake_rate": 0.0,
                "passed": False,
            },
            "examples/stable/tests/test_script.py": {
                "project_path": "examples/stable",
                "test_path": "examples/stable/tests/test_script.py",
                "trials": 3,
                "runtime_sum": 9.428875000000003,
                "avg_runtime": 3.1429583333333344,
                "passes": 0,
                "pass_rate": 0.0,
                "fails": 3,
                "fail_rate": 1.0,
                "flakes": 0,
                "flake_rate": 0.0,
                "passed": False,
            },
            "examples/stable/tests/test_apple.py": {
                "project_path": "examples/stable",
                "test_path": "examples/stable/tests/test_apple.py",
                "trials": 3,
                "runtime_sum": 10.18191700000004,
                "avg_runtime": 3.3939723333333465,
                "passes": 0,
                "pass_rate": 0.0,
                "fails": 3,
                "fail_rate": 1.0,
                "flakes": 0,
                "flake_rate": 0.0,
                "passed": False,
            },
        }
    }


def test_find_flakiest_modules():
    module_one = Module(name="one")
    module_one.flake_rate = 0.1
    module_two = Module(name="two")
    module_two.flake_rate = 0.2
    module_three = Module(name="three")
    module_three.flake_rate = 0.6
    module_four = Module(name="four")
    module_four.flake_rate = 0.4
    module_five = Module(name="five")
    module_five.flake_rate = 0.3

    # test a bunch of even-numbered permutations
    input_module_collection = ModuleCollection(
        runtimes=[], modules=[module_three, module_one, module_two, module_four]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]

    input_module_collection = ModuleCollection(
        runtimes=[], modules=[module_two, module_three, module_one, module_four]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]

    input_module_collection = ModuleCollection(
        runtimes=[], modules=[module_two, module_four, module_three, module_one]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]

    input_module_collection = ModuleCollection(
        runtimes=[], modules=[module_two, module_one, module_four, module_three]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]

    # test a bunch of odd-numbered permutations
    input_module_collection = ModuleCollection(
        runtimes=[], modules=[module_three, module_five, module_one, module_two, module_four]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]

    input_module_collection = ModuleCollection(
        runtimes=[], modules=[module_two, module_five, module_three, module_one, module_four]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]

    input_module_collection = ModuleCollection(
        runtimes=[], modules=[module_two, module_four, module_three, module_five, module_one]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]

    input_module_collection = ModuleCollection(
        runtimes=[], modules=[module_two, module_one, module_five, module_four, module_three]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]


def test_find_flakiest_modules_empty():
    output_rate, output_modules = analyze.find_flakiest_modules(
        ModuleCollection(modules=[], runtimes=[])
    )
    assert output_rate == None
    assert output_modules == []


def test_find_flakiest_modules_one_entry():
    module = Module(name="one")
    module.flake_rate = 0.5
    output_rate, output_modules = analyze.find_flakiest_modules(
        ModuleCollection(modules=[module], runtimes=[])
    )
    assert output_rate == 0.5
    assert output_modules == ["one"]


def test_find_flakiest_modules_all_zeros():
    module_one = Module(name="one")
    module_one.flake_rate = 0
    module_two = Module(name="two")
    module_two.flake_rate = 0
    module_three = Module(name="three")
    module_three.flake_rate = 0
    module_four = Module(name="four")
    module_four.flake_rate = 0

    input_module_collection = ModuleCollection(
        runtimes=[], modules=[module_three, module_one, module_two, module_four]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0

    expected_modules = ["three", "one", "two", "four"]
    assert output_modules == expected_modules


def test_find_flakiest_modules_duplicate():
    module_one = Module(name="one")
    module_one.flake_rate = 0.1
    module_two = Module(name="two")
    module_two.flake_rate = 0.4
    module_three = Module(name="three")
    module_three.flake_rate = 0.6
    module_four = Module(name="four")
    module_four.flake_rate = 0.4
    module_five = Module(name="five")
    module_five.flake_rate = 0.3

    input_module_collection = ModuleCollection(
        runtimes=[], modules=[module_three, module_one, module_two, module_four, module_five]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]


def test_find_make_flake_rate_duplicate_max():
    module_one = Module(name="one")
    module_one.flake_rate = 0.1
    module_two = Module(name="two")
    module_two.flake_rate = 0.6
    module_three = Module(name="three")
    module_three.flake_rate = 0.6
    module_four = Module(name="four")
    module_four.flake_rate = 0.4
    module_five = Module(name="five")
    module_five.flake_rate = 0.3

    input_module_collection = ModuleCollection(
        runtimes=[], modules=[module_three, module_one, module_two, module_four, module_five]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == [dataclasses.asdict(module_three), dataclasses.asdict(module_two)]


def test_find_flakiest_modules_super_long():
    input_module_collection = ModuleCollection(runtimes=[], modules=[])
    for i in range(0, 10000):
        module = Module(name="looong")
        module.flake_rate = randint(1, 1000) // 1001
        input_module_collection.modules.append(module)

    winner = Module(name="winner")
    winner.flake_rate = 10
    input_module_collection.modules.insert(randint(2, 999), winner)

    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == winner.flake_rate
    assert len(output_modules) == 1

    output_module = output_modules.pop()
    assert output_module == "winner"


def test_find_slowest_modules_stable(stable_mock):
    expected = [
        {"blue": {"precise_runtime_ms": 47.39793066666668, "floored_runtime_ms": 47}},
        {"banana": {"precise_runtime_ms": 49.28530566666667, "floored_runtime_ms": 49}},
        {"amazing": {"precise_runtime_ms": 69.96991666666668, "floored_runtime_ms": 69}},
    ]
    stats = analyze.BubblewrapModuleStats(
        modules=stable_mock.modules,
        runtimes=stable_mock.runtimes,
        flakiest_modules=[],
        slowest_modules=[],
    )
    output = stats.find_slowest(3)
    assert output == expected


def test_find_slowest_modules_flake(flake_mock):
    expected = [
        {"alligator": {"precise_runtime_ms": 33.639694333333324, "floored_runtime_ms": 33}},
        {"awesome": {"precise_runtime_ms": 55.760194333333325, "floored_runtime_ms": 55}},
    ]
    stats = analyze.BubblewrapModuleStats(
        modules=flake_mock.modules,
        runtimes=flake_mock.runtimes,
        flakiest_modules=[],
        slowest_modules=[],
    )
    output = stats.find_slowest(3)
    assert output == expected


# examples/stable/tests/test_banana.py
def test_recommend_tests_for_optimization(stable_test_results_mock):
    expected = "examples/stable/tests/test_banana.py"
    output = analyze.recommend_tests_for_optimization(stable_test_results_mock)

    assert isinstance(output, set)
    assert expected in output
