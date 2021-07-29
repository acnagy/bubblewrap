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
        # runtimes will be in ms for easier reading
        runtime *= 1000
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
class Results:
    tests: None  # Dict{test_path: test_result}

    def get(self, test_path: str) -> Test:
        return self.tests.get(test_path)

    def put(self, test_path: str, result: Test):
        self.tests[test_path] = result


def run_tests(path: str, trials: int, collected_tests: List[str]) -> Dict:
    """
    This function intakes the tests collected by the collect.collect_tests() function,
    instantiates containing objects, and executes summaries of both tests and modules
    """
    results = Results(tests={})
    for test_path in collected_tests:
        # modules will tend to be interdependent, so we'll probably come across tests
        # we've already run, hence the results cache
        if results.get(test_path):
            logger.info(f"Already ran test: {test_path}")
        else:
            result = Test(project_path=path, trials=trials, test_path=test_path)
            logger.info(f"Running test: {test_path}")
            # actually run the tests $trials number of times
            result.run()
            results.put(test_path, result)
    return asdict(results)
