import logging
import json

from typing import List, Dict, Set
from dataclasses import dataclass, asdict
from math import floor

from summarize import Module, ModuleCollection

logger = logging.getLogger(__name__)


"""
Represents a collection Modules, with metadata on which modules are the flakiest and the rate at which the
tests that cover those modules flake.
"""


@dataclass
class BubblewrapModuleStats:
    flakiest_modules: None  # List[Module]
    slowest_modules: None  # List[Module]
    runtimes: None  # List[Module]
    modules: None  # List[Module]
    max_flake_rate: float = None
    runtimes_result_count: int = None

    def find_flakiest(self):
        """
        This method finds the flakiest tests and the flake rate from a complete list of Modules -- we don't
        build this incrementally, though arguably, we could
        """
        modules_list = self.modules
        self._search_for_flakiest(modules_list)

    def find_slowest(self, top_n: int):
        """
        returns a sorted + truncated dict of Modules, ordered by average runtime, but it doesn't have to be
        exactly in order. This is a kind of fuzzy sort where we're returning a list of modules sorted to the 3rd
        decimal place, because of the nature the problem - more precision than that really doesn't make sense
        (these are unit tests -- they're not gonna be precise to the microseconds)
        """

        # counts the number of times each floored runtime appears in the results, converting
        # self.runtimes to a dict of {runtime: appearance_count}
        self._count_modules_by_runtime()

        # counts the number of results we want to return -- this is top_n, floored up to account
        # for ties, and sets up self.runtimes to define the allowed results list index for each
        # runtime that appears, converting self.runtimes to {runtime: (start, end)}
        self._count_expected_results(top_n)

        results = [None] * self.runtimes_result_count
        for module in self.modules:
            floored = floor(module.runtime)
            start, end = self.runtimes[floored]
            if end < self.runtimes_result_count:
                results[end] = {
                    module.name: {
                        "precise_runtime_ms": module.runtime,
                        "floored_runtime_ms": floored,
                    }
                }
                self.runtimes[floored] = [start, end - 1]
        self.slowest_modules = results
        return self.slowest_modules

    def _search_for_flakiest(self, modules: List):
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
            self._search_for_flakiest(modules[: midpt + 1])
            self._search_for_flakiest(modules[midpt + 1 :])
        return

    def _count_modules_by_runtime(self):
        """
        count the number of items in each runtime bucket -- build this dict in reverse order
        so we can pop off the end (more efficient)
        """
        logger.info("counting the modules by floored runtime")
        self.runtimes = {l: 0 for l in self.runtimes}
        for module in self.modules:
            self.runtimes[floor(module.runtime)] += 1
        logger.info(f"done counting")

    def _count_expected_results(self, top_n: int):
        """
        do prep work - we'll need to know the start/stop indices in the returned results list
        for the runtimes that we care about, and the number of results that we want to return,
        which will top_n, including all ties
        """
        logger.info(
            "prepping expected result count + which indices account for sorted floored runtime buckets"
        )
        result_count, indices_counted = 0, 0
        for runtime, count in self.runtimes.items():
            if result_count < top_n:
                result_count += count

            self.runtimes[runtime] = [indices_counted, indices_counted + count - 1]
            indices_counted += count
        self.runtimes_result_count = result_count
        logger.info(f"done: will return {result_count} results")


"""
Aggregates raw test results so we can do things like make recommendations for specific tests to optimize
"""


class BubblewrapTestStats:
    def __init__(self, tests):
        self.tests = tests
        self.total_runtime = int(sum([t["runtime_sum"] for t in self.tests]))
        self.cutoff = self.total_runtime // 2
        self.cache = []

    def find_cutoff_optimized_set(self) -> Set[str]:
        """
        prep cache and find largest number of tests that get close to 50%  - returns the test paths comprising
        this optimized set of results
        """
        self._prep_cache()
        optimized_set = self._find_cutoff_optimized_set(len(self.tests) - 1, self.cutoff)
        return optimized_set[1]

    def _prep_cache(self):
        """
        builds a table to store prior solutions to the optimization problem for the largest set of tests that
        account for up to 50% of the total runtime
        """
        self.cache = [[None] * (self.cutoff + 1) for _ in range(len(self.tests) + 1)]

    def _find_cutoff_optimized_set(self, test_index, margin_left):
        """
        recursive helper function for searching for potential test results to add to our optimal solution
        """
        # check if we're at the end or have already passed by here
        if test_index == 0:
            return [0, set()]
        if self.cache[test_index][margin_left] != None:
            return self.cache[test_index][margin_left]

        new_runtime = self.tests[test_index]["runtime_sum"]
        new_test = self.tests[test_index]["path"]
        if new_runtime > margin_left:
            # skip this bc the runtime pushes us over the cutoff
            result = self._find_cutoff_optimized_set(test_index - 1, margin_left)
        else:
            # figure out which is better - including this new runtime or skipping over it
            included = self._find_cutoff_optimized_set(test_index - 1, margin_left - new_runtime)
            included[0] += 1  # increment this to account for including a new test in output set
            not_included = self._find_cutoff_optimized_set(test_index - 1, margin_left)
            result = max(included, not_included, key=lambda t: t[1])

            # if we're going to return the variant where we include the new test, then insert
            # into the optimized result test of test paths that we're building
            if result == included:
                included[1].add(new_test)

            # memoize the new result that we've calculated for when we pass by here again
            self.cache[test_index][margin_left] = result
        return result


def find_flakiest_modules(module_collection: ModuleCollection) -> (float, Dict):
    """
    Wraps the functionality on BubblewrapModuleStats that searches for the flakiest modules
    """
    stats = BubblewrapModuleStats(
        modules=module_collection.modules,
        runtimes=module_collection.runtimes,
        flakiest_modules=[],
        slowest_modules=[],
    )
    stats.find_flakiest()

    rate = stats.max_flake_rate
    stats = asdict(stats)
    stats = stats.pop("flakiest_modules", None)
    modules = [s["name"] for s in stats]
    return rate, modules


def find_slowest_modules(module_collection: ModuleCollection) -> List[Dict]:
    """
    Wraps the functionality on BubblewrapModuleStats for finding the top_n slowest modules
    """
    stats = BubblewrapModuleStats(
        modules=module_collection.modules,
        runtimes=module_collection.runtimes,
        flakiest_modules=[],
        slowest_modules=[],
    )
    logger.info(
        "calling analyze.find_slowest_modules(execution_results) to find the top 3 or so slow modules"
    )
    return stats.find_slowest(3)


def recommend_tests_for_optimization(test_results: Dict) -> Set[str]:
    """
    Makes a recommendation of a set of tests to consider optimizing. This set accounts for around 50% of
    the time it takes to run tests. This set is *either* the SMALLER of the two possibilities:
    (1) a set that comprises up to 50% of the test execution time
    (2) the complement set of tests
    OR if sets (1) and (2) have the same length, then it is whichever of these accounts for at least 50%
    of the test runtime. The goal here is to make a workable recommendation, considering that humans want
    manageable goals and humans will be doing this optimization.
    """
    test_results = test_results["tests"]
    tests, total_runtime = [], 0
    for path, results in test_results.items():
        tests.append(
            {"path": results["test_path"], "runtime_sum": int(results["runtime_sum"])}
        )  # convert from ms, round to an int (sorry)
    stats = BubblewrapTestStats(tests=tests)

    test_paths = set([t["path"] for t in tests])
    up_to_cutoff = stats.find_cutoff_optimized_set()
    rest_of_tests = test_paths - up_to_cutoff

    if len(up_to_cutoff) == len(rest_of_tests):
        # up_to_cutoff is optimized for no more than 50% of the total runtime, if the lengths
        # this list and the complement are the same, then the complement is going to account
        # at least 50% of the runtime -- a larger fraction
        return rest_of_tests

    # now we just want to recommend the more managable (aka smaller) set that accounts for
    # approximately 50% of the time we spend running tests -- people like to fix accomplishable tasks
    smaller = min(len(up_to_cutoff), len(rest_of_tests))
    if smaller == len(up_to_cutoff):
        return up_to_cutoff
    return rest_of_tests
