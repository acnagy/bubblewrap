import pytest
import os
import dataclasses

import analyze

from random import randint

from run import ModuleCollection, Module, Test


# there are nicer ways of doing this
@pytest.fixture()
def stable_mock():
    root = os.getcwd()
    return ModuleCollection(
        modules=[
            Module(
                name="blue",
                test_results=[
                    Test(
                        project_path="{root}/examples/stable",
                        test_path="{root}/examples/stable/tests/test_banana.py",
                        trials=3,
                        runtime_sum=0.08013995900000004,
                        avg_runtime=0.02671331966666668,
                        passes=3,
                        pass_rate=1.0,
                        fails=0,
                        fail_rate=0.0,
                        flakes=0,
                        flake_rate=0.0,
                        passed=True,
                    ),
                    Test(
                        project_path="{root}/examples/stable",
                        test_path="{root}/examples/stable/tests/test_apple.py",
                        trials=3,
                        runtime_sum=0.062053833,
                        avg_runtime=0.020684611000000002,
                        passes=3,
                        pass_rate=1.0,
                        fails=0,
                        fail_rate=0.0,
                        flakes=0,
                        flake_rate=0.0,
                        passed=True,
                    ),
                ],
                flake_rate=0.0,
                runtime=0.04739793066666668,
            ),
            Module(
                name="banana",
                test_results=[
                    Test(
                        project_path="{root}/examples/stable",
                        test_path="{root}/examples/stable/tests/test_banana.py",
                        trials=3,
                        runtime_sum=0.08013995900000004,
                        avg_runtime=0.02671331966666668,
                        passes=3,
                        pass_rate=1.0,
                        fails=0,
                        fail_rate=0.0,
                        flakes=0,
                        flake_rate=0.0,
                        passed=True,
                    ),
                    Test(
                        project_path="{root}/examples/stable",
                        test_path="{root}/examples/stable/tests/test_amazing.py",
                        trials=3,
                        runtime_sum=0.06771595799999997,
                        avg_runtime=0.02257198599999999,
                        passes=3,
                        pass_rate=1.0,
                        fails=0,
                        fail_rate=0.0,
                        flakes=0,
                        flake_rate=0.0,
                        passed=True,
                    ),
                ],
                flake_rate=0.0,
                runtime=0.04928530566666667,
            ),
            Module(
                name="amazing",
                test_results=[
                    Test(
                        project_path="{root}/examples/stable",
                        test_path="{root}/examples/stable/tests/test_banana.py",
                        trials=3,
                        runtime_sum=0.08013995900000004,
                        avg_runtime=0.02671331966666668,
                        passes=3,
                        pass_rate=1.0,
                        fails=0,
                        fail_rate=0.0,
                        flakes=0,
                        flake_rate=0.0,
                        passed=True,
                    ),
                    Test(
                        project_path="{root}/examples/stable",
                        test_path="{root}/examples/stable/tests/test_amazing.py",
                        trials=3,
                        runtime_sum=0.06771595799999997,
                        avg_runtime=0.02257198599999999,
                        passes=3,
                        pass_rate=1.0,
                        fails=0,
                        fail_rate=0.0,
                        flakes=0,
                        flake_rate=0.0,
                        passed=True,
                    ),
                    Test(
                        project_path="{root}/examples/stable",
                        test_path="{root}/examples/stable/tests/test_apple.py",
                        trials=3,
                        runtime_sum=0.062053833,
                        avg_runtime=0.020684611000000002,
                        passes=3,
                        pass_rate=1.0,
                        fails=0,
                        fail_rate=0.0,
                        flakes=0,
                        flake_rate=0.0,
                        passed=True,
                    ),
                ],
                flake_rate=0.0,
                runtime=0.06996991666666667,
            ),
            Module(
                name="script",
                test_results=[
                    Test(
                        project_path="{root}/examples/stable",
                        test_path="{root}/examples/stable/tests/test_script.py",
                        trials=3,
                        runtime_sum=0.061552457000000116,
                        avg_runtime=0.020517485666666706,
                        passes=3,
                        pass_rate=1.0,
                        fails=0,
                        fail_rate=0.0,
                        flakes=0,
                        flake_rate=0.0,
                        passed=True,
                    ),
                    Test(
                        project_path="{root}/examples/stable",
                        test_path="{root}/examples/stable/tests/test_apple.py",
                        trials=3,
                        runtime_sum=0.062053833,
                        avg_runtime=0.020684611000000002,
                        passes=3,
                        pass_rate=1.0,
                        fails=0,
                        fail_rate=0.0,
                        flakes=0,
                        flake_rate=0.0,
                        passed=True,
                    ),
                ],
                flake_rate=0.0,
                runtime=0.04120209666666671,
            ),
            Module(
                name="apple",
                test_results=[
                    Test(
                        project_path="{root}/examples/stable",
                        test_path="{root}/examples/stable/tests/test_apple.py",
                        trials=3,
                        runtime_sum=0.062053833,
                        avg_runtime=0.020684611000000002,
                        passes=3,
                        pass_rate=1.0,
                        fails=0,
                        fail_rate=0.0,
                        flakes=0,
                        flake_rate=0.0,
                        passed=True,
                    )
                ],
                flake_rate=0.0,
                runtime=0.020684611000000002,
            ),
        ],
        runtimes=[0.02, 0.04, 0.05, 0.07],
    )


@pytest.fixture
def flake_mock():
    root = os.getcwd()
    return ModuleCollection(
        modules=[
            Module(
                name="alligator",
                test_results=[
                    Test(
                        project_path=f"{root}/examples/flake",
                        test_path=f"{root}/examples/flake/tests/test_alligator.py",
                        trials=3,
                        runtime_sum=0.10091908299999997,
                        avg_runtime=0.033639694333333324,
                        passes=0,
                        pass_rate=0.0,
                        fails=3,
                        fail_rate=1.0,
                        flakes=0,
                        flake_rate=0.0,
                        passed=False,
                    )
                ],
                flake_rate=0.0,
                runtime=0.033639694333333324,
            ),
            Module(
                name="awesome",
                test_results=[
                    Test(
                        project_path=f"{root}/examples/flake",
                        test_path=f"{root}/examples/flake/tests/test_alligator.py",
                        trials=3,
                        runtime_sum=0.10091908299999997,
                        avg_runtime=0.033639694333333324,
                        passes=0,
                        pass_rate=0.0,
                        fails=3,
                        fail_rate=1.0,
                        flakes=0,
                        flake_rate=0.0,
                        passed=False,
                    ),
                    Test(
                        project_path=f"{root}/examples/flake",
                        test_path=f"{root}/examples/flake/tests/test_awesome.py",
                        trials=3,
                        runtime_sum=0.06636150000000002,
                        avg_runtime=0.022120500000000005,
                        passes=2,
                        pass_rate=0.6666666666666666,
                        fails=1,
                        fail_rate=0.3333333333333333,
                        flakes=2,
                        flake_rate=0.6666666666666666,
                        passed=False,
                    ),
                ],
                flake_rate=0.6666666666666666,
                runtime=0.055760194333333325,
            ),
        ],
        runtimes=[0.03, 0.06],
    )


def test_find_flakiest_modules():
    module_one = analyze.Module(name="one", test_results=[])
    module_one.flake_rate = 0.1
    module_two = analyze.Module(name="two", test_results=[])
    module_two.flake_rate = 0.2
    module_three = analyze.Module(name="three", test_results=[])
    module_three.flake_rate = 0.6
    module_four = analyze.Module(name="four", test_results=[])
    module_four.flake_rate = 0.4
    module_five = analyze.Module(name="five", test_results=[])
    module_five.flake_rate = 0.3

    # test a bunch of even-numbered permutations
    input_module_collection = analyze.ModuleCollection(
        runtimes=[], modules=[module_three, module_one, module_two, module_four]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]

    input_module_collection = analyze.ModuleCollection(
        runtimes=[], modules=[module_two, module_three, module_one, module_four]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]

    input_module_collection = analyze.ModuleCollection(
        runtimes=[], modules=[module_two, module_four, module_three, module_one]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]

    input_module_collection = analyze.ModuleCollection(
        runtimes=[], modules=[module_two, module_one, module_four, module_three]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]

    # test a bunch of odd-numbered permutations
    input_module_collection = analyze.ModuleCollection(
        runtimes=[], modules=[module_three, module_five, module_one, module_two, module_four]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]

    input_module_collection = analyze.ModuleCollection(
        runtimes=[], modules=[module_two, module_five, module_three, module_one, module_four]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]

    input_module_collection = analyze.ModuleCollection(
        runtimes=[], modules=[module_two, module_four, module_three, module_five, module_one]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]

    input_module_collection = analyze.ModuleCollection(
        runtimes=[], modules=[module_two, module_one, module_five, module_four, module_three]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]


def test_find_flakiest_modules_empty():
    output_rate, output_modules = analyze.find_flakiest_modules(
        analyze.ModuleCollection(modules=[], runtimes=[])
    )
    assert output_rate == None
    assert output_modules == []


def test_find_flakiest_modules_one_entry():
    module = analyze.Module(name="one", test_results=[])
    module.flake_rate = 0.5
    output_rate, output_modules = analyze.find_flakiest_modules(
        analyze.ModuleCollection(modules=[module], runtimes=[])
    )
    assert output_rate == 0.5
    assert output_modules == ["one"]


def test_find_flakiest_modules_all_zeros():
    module_one = analyze.Module(name="one", test_results=[])
    module_one.flake_rate = 0
    module_two = analyze.Module(name="two", test_results=[])
    module_two.flake_rate = 0
    module_three = analyze.Module(name="three", test_results=[])
    module_three.flake_rate = 0
    module_four = analyze.Module(name="four", test_results=[])
    module_four.flake_rate = 0

    input_module_collection = analyze.ModuleCollection(
        runtimes=[], modules=[module_three, module_one, module_two, module_four]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0

    expected_modules = ["three", "one", "two", "four"]
    assert output_modules == expected_modules


def test_find_flakiest_modules_duplicate():
    module_one = analyze.Module(name="one", test_results=[])
    module_one.flake_rate = 0.1
    module_two = analyze.Module(name="two", test_results=[])
    module_two.flake_rate = 0.4
    module_three = analyze.Module(name="three", test_results=[])
    module_three.flake_rate = 0.6
    module_four = analyze.Module(name="four", test_results=[])
    module_four.flake_rate = 0.4
    module_five = analyze.Module(name="five", test_results=[])
    module_five.flake_rate = 0.3

    input_module_collection = analyze.ModuleCollection(
        runtimes=[], modules=[module_three, module_one, module_two, module_four, module_five]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == ["three"]


def test_find_make_flake_rate_duplicate_max():
    module_one = analyze.Module(name="one", test_results=[])
    module_one.flake_rate = 0.1
    module_two = analyze.Module(name="two", test_results=[])
    module_two.flake_rate = 0.6
    module_three = analyze.Module(name="three", test_results=[])
    module_three.flake_rate = 0.6
    module_four = analyze.Module(name="four", test_results=[])
    module_four.flake_rate = 0.4
    module_five = analyze.Module(name="five", test_results=[])
    module_five.flake_rate = 0.3

    input_module_collection = analyze.ModuleCollection(
        runtimes=[], modules=[module_three, module_one, module_two, module_four, module_five]
    )
    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == 0.6
    assert output_modules == [dataclasses.asdict(module_three), dataclasses.asdict(module_two)]


def test_find_flakiest_modules_super_long():
    input_module_collection = analyze.ModuleCollection(runtimes=[], modules=[])
    for i in range(0, 10000):
        module = analyze.Module(name="looong", test_results=[])
        module.flake_rate = randint(1, 1000) // 1001
        input_module_collection.modules.append(module)

    winner = analyze.Module(name="winner", test_results=[])
    winner.flake_rate = 10
    input_module_collection.modules.insert(randint(2, 999), winner)

    output_rate, output_modules = analyze.find_flakiest_modules(input_module_collection)
    assert output_rate == winner.flake_rate
    assert len(output_modules) == 1

    output_module = output_modules.pop()
    assert output_module == "winner"


def test_find_slowest_modules_stable(stable_mock):
    expected = [
        {"apple": {"precise_runtime": 0.020684611000000002, "rounded_runtime": 0.02}},
        {"script": {"precise_runtime": 0.04120209666666671, "rounded_runtime": 0.04}},
        {"banana": {"precise_runtime": 0.04928530566666667, "rounded_runtime": 0.05}},
        {"blue": {"precise_runtime": 0.04739793066666668, "rounded_runtime": 0.05}},
    ]
    stats = analyze.BubblewrapStats(
        modules=stable_mock.modules,
        runtimes=stable_mock.runtimes,
        flakiest_modules=[],
        slowest_modules=[],
    )
    output = stats.find_slowest(3)
    assert output == expected


def test_find_slowest_modules_flake(flake_mock):
    expected = [
        {"alligator": {"precise_runtime": 0.033639694333333324, "rounded_runtime": 0.03}},
        {"awesome": {"precise_runtime": 0.055760194333333325, "rounded_runtime": 0.06}},
    ]
    stats = analyze.BubblewrapStats(
        modules=flake_mock.modules,
        runtimes=flake_mock.runtimes,
        flakiest_modules=[],
        slowest_modules=[],
    )
    output = stats.find_slowest(3)
    assert output == expected
