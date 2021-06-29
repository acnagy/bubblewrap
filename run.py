import pytest
import time
import logging
import os
import sys
import dataclasses
import json


from typing import List, Dict
from dataclasses import dataclass
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
    latency_sum: int = 0
    avg_latency: float = 0.0
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
            succeeded, latency = self._test(test_dir)
            if succeeded:
                self.passes += 1
            else:
                self.fails += 1
            self.latency_sum += latency
            remaining -= 1

        # reset sys defaults so we don't cause unnecessary side effects
        os.chdir(working_dir)
        sys.stdout, sys.stderr = old_stdout, old_stderr

        # summarize trial runs
        self._calculate()

    def _test(self, test_dir: str) -> (bool, int):  # pass, fail, latency
        """
        this is the method where we actually call pytest for one atomic unit test
        """
        test = os.path.relpath(self.test_path, test_dir)
        start = time.perf_counter()
        retcode = pytest.main([test, "--rootdir", self.project_path])
        latency = time.perf_counter() - start
        return retcode is ExitCode.OK, latency

    def _calculate(self):
        self.avg_latency = self.latency_sum / self.trials
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
    latency: float = 0.0

    def summarize(self):
        if self.test_results is None:
            self.test_results = []
        for result in self.test_results:
            self.latency += result.latency_sum
            self.flake_rate += result.flakes
        # assumes that all tests are executed with the same number of trials
        # which is currently safe, but this'll get wonky if we can vary that param
        self.latency /= result.trials
        self.flake_rate /= result.trials


"""
Represents a collection Modules, with metadata on which modules are the flakiest and the rate at which the
tests that cover those modules flake.
"""


@dataclass
class ModuleList:
    flakiest_modules: None
    modules: None
    max_flake_rate: float = None

    def find_flakiest(self):
        """
        This method finds the flakiest tests and the flake rate from a complete list of Modules -- we don't
        build this incrementally, though arguably, we could
        """
        modules_list = self.modules
        self._search(modules_list)

    def _search(self, modules: List):
        """
        recursively search through the unsorted lists of completed modules to find the flaky tests we want
        """
        if not modules:
            return

        # if we're at an array of 1, we can assess the rate for whether it's the maximum flake rate
        # aka whether we've found an immediately solvable outcome
        if len(modules) == 1:
            module = modules.pop()
            if self.max_flake_rate is None or module.flake_rate > self.max_flake_rate:
                self.max_flake_rate = module.flake_rate
                self.flakiest_modules = [module]
            elif module.flake_rate == self.max_flake_rate:
                self.flakiest_modules.append(module)
            return

        midpt = (len(modules) - 1) // 2
        # if there are 2 elements in this array, midpt will be 0
        if midpt >= 0:
            # shift up by 1 to handle when midpt = 0 because we'll slice off the remaining modules to search
            self._search(modules[: midpt + 1])
            self._search(modules[midpt + 1 :])
        return


def run_tests(path: str, trials: int, collected: Dict[str, List[str]]) -> List[Module]:
    """
    This function intakes the tests collected by the collect.collect_tests() function,
    instantiates containing objects, and executes summaries of both tests and modules
    """
    modules, cache = [], Cache(results={})
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
        logger.info(
            f"Calculated {module_name} results: {json.dumps(dataclasses.asdict(module), indent=2)}"
        )
        modules.append(module)
    return modules


def find_flakiest_tests(modules: List[Module]) -> (float, Dict):
    """
    Wraps the functionality on ModulesList that searches for the flakiest tests
    """
    modules = ModuleList(modules=modules, flakiest_modules=[])
    modules.find_flakiest()

    rate = modules.max_flake_rate
    modules = dataclasses.asdict(modules)
    modules = modules.pop("flakiest_modules", None)
    return rate, modules
