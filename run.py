import pytest
import time
import logging
import os
import sys
import json


from typing import List, Dict
from dataclasses import dataclass, asdict
from pytest import ExitCode

logger = logging.getLogger(__name__)
red = "\u001b[31m"
green = "\u001b[32m"
reset = "\u001b[0m"


"""
Represents a collection of runs of a unit test, including methods to run these
tests repeatedly and calculate summary results
"""


@dataclass
class Test:
    project_path: str = ""
    test_path: str = ""
    trials: int = 0
    runtime_sum: int = 0
    avg_runtime: float = 0.0
    passes: int = 0
    pass_rate: float = 0.0
    fails: int = 0
    fail_rate: float = 0.0
    flakes: int = 0
    flake_rate: float = 0.0
    passed: bool = False

    def run(self):
        """
        run this test $trials numbers of times and summarize
        """

        # suppress stdout, stderror for clearer logs
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = open(os.devnull, "w"), open(os.devnull, "w")

        # set working dir and test dir so pytest can collect the files it needs
        # we'll reset this later, so python continues to work out of the directory
        # where bubblewrap was called
        working_dir = os.getcwd()
        if self.project_path == working_dir:
            test_dir = working_dir
        else:
            test_dir = os.path.join(working_dir, self.project_path)
        os.chdir(test_dir)

        # trials is selected by the user
        remaining = self.trials
        while remaining:
            succeeded, runtime = self._test(test_dir)
            if succeeded:
                self.passes += 1
            else:
                self.fails += 1
            self.runtime_sum += runtime
            remaining -= 1

        # reset sys defaults so we don't cause unnecessary side effects
        os.chdir(working_dir)
        sys.stdout, sys.stderr = old_stdout, old_stderr

        # summarize trial runs
        self._calculate()

    def _test(self, test_dir: str) -> (bool, int):  # pass, fail, runtime
        """
        this is the method where we actually call pytest for one atomic unit test
        """
        test = os.path.relpath(self.test_path, test_dir)
        start = time.perf_counter()
        retcode = pytest.main([test, "--rootdir", self.project_path])
        runtime = time.perf_counter() - start
        return retcode is ExitCode.OK, runtime

    def _calculate(self):
        self.avg_runtime = self.runtime_sum / self.trials
        self.pass_rate = self.passes / self.trials
        self.fail_rate = self.fails / self.trials
        self.passed = self.pass_rate >= 0.75

        # "flakes" are defined as test results that were the opposite of what "should" have happened
        # so, if in general, this test fails, then the passes are considered flakes, and vice versa
        self.flakes = self.fails if self.passed else self.passes
        self.flake_rate = self.flakes / self.trials


"""
Represents a simple cache of completed Tests, so we don't have to re-run these replicated, summarized
tests so we don't have to keep recalcuating the same (expensive) test runs
"""


@dataclass
class Cache:
    results: None  # Dict{test_path: test_result}

    def get(self, test_path: str) -> Test:
        return self.results.get(test_path)

    def put(self, test_path: str, result: Test):
        self.results[test_path] = result


"""
Represents an application module and the collected, executed, and summarized unit tests that cover it.
"""


@dataclass
class Module:
    name: str
    test_results: None  # List[all_test_results]
    flake_rate: float = 0.0
    runtime: float = 0.0

    def summarize(self):
        if self.test_results is None:
            self.test_results = []
        for result in self.test_results:
            self.runtime += result.runtime_sum
            self.flake_rate += result.flakes
        # assumes that all tests are executed with the same number of trials
        # which is currently safe, but this'll get wonky if we can vary that param
        self.runtime /= result.trials
        self.flake_rate /= result.trials


"""
Represents a whole executions' worth of modules and the state -- sorted rounded runtimes -- that we
need to maintain for our fuzy sort later
"""


@dataclass
class ModuleCollection:
    modules: None  # List[Module]
    runtimes: None  # sorted List of runtimes

    def add(self, module: Module):
        """
        add new module to the list, and insert it's rounded runtime where appropriate
        """
        self.modules.append(module)
        self._sort_runtime(module)

    def _sort_runtime(self, module: Module):
        """
        sort the runtimes, rounded. We'll use this in the analysis phase for returning
        the modules with the slowest tests, including ties
        """
        runtime = round_runtime(module.runtime)
        if not self.runtimes:
            self.runtimes.append(runtime)
        else:
            index = self._runtimes_insert_index(runtime, 0, len(self.runtimes) - 1)
            if index is not None:
                self.runtimes.insert(index, runtime)

    def _runtimes_insert_index(self, runtime, low: int, high: int):
        """
        this is a modified binary search so we can find where to insert new runtimes and maintain
        a sorted order of modules' test runtimes
        """
        if runtime < self.runtimes[0]:
            return 0

        if runtime > self.runtimes[len(self.runtimes) - 1]:
            return len(self.runtimes)  # we'll want to insert at the end

        midpt = (high + low) // 2
        # this runtime value is already accounted for
        if self.runtimes[midpt] == runtime or low >= high:
            return None

        # bridges the middle - runtime is between previous and midpt, or midpt and next
        if midpt - 1 >= 0 and self.runtimes[midpt - 1] < runtime < self.runtimes[midpt]:
            return midpt
        if (
            midpt + 1 <= len(self.runtimes) - 1
            and self.runtimes[midpt] < runtime < self.runtimes[midpt + 1]
        ):
            return midpt + 1

        # recurse in the left (lower) or right (upper) wing of unsearched runtimes
        if runtime < self.runtimes[midpt]:
            return self._runtimes_insert_index(runtime, low, midpt - 1)
        else:
            return self._runtimes_insert_index(runtime, midpt + 1, high)


def run_tests(path: str, trials: int, collected: Dict[str, List[str]]) -> List[Module]:
    """
    This function intakes the tests collected by the collect.collect_tests() function,
    instantiates containing objects, and executes summaries of both tests and modules
    """
    modules, cache = ModuleCollection(modules=[], runtimes=[]), Cache(results={})
    for module_name, tests in collected.items():
        module = Module(name=module_name, test_results=[])
        for test_path in tests:
            # modules will tend to be interdependent, so we'll probably come across tests
            # we've already run, hence the results cache
            if cache.get(test_path):
                logger.info(f"Already ran test: {test_path}")
                result = cache.get(test_path)
            else:
                result = Test(project_path=path, trials=trials, test_path=test_path)
                logger.info(f"Running test: {test_path}")
                # actually run the tests $trials number of times
                result.run()
                cache.put(test_path, result)

            stats = f"success rate: {result.pass_rate}, flake_rate: {result.flake_rate}"
            if result.passed:
                logger.info(f"test {path} {green}PASSED{reset}; {stats}")
            else:
                logger.warn(f"test {path} {red}FAILED{reset}; {stats}")

            module.test_results.append(result)

        module.summarize()
        logger.info(f"Calculated {module_name} results")
        modules.add(module)
    return modules


def round_runtime(runtime: int) -> float:
    """
    helper so we're only setting how  many decimals to round to in one place
    """
    return round(runtime, 2)
