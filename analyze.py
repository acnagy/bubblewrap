import logging
import json

from typing import List, Dict
from dataclasses import dataclass, asdict

from run import Module, ModuleCollection, round_runtime

logger = logging.getLogger(__name__)


"""
Represents a collection Modules, with metadata on which modules are the flakiest and the rate at which the
tests that cover those modules flake.
"""


@dataclass
class BubblewrapStats:
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

        # counts the number of times each rounded rime appears in the results, converting
        # self.runtimes to a dict of {runtime: appearance_count}
        self._count_modules_by_runtime()

        # counts the number of results we want to return -- this is top_n, rounded up to account
        # for ties, and sets up self.runtimes to define the allowed results list index for each
        # runtime that appears, converting self.runtimes to {runtime: (start, end)}
        self._count_expected_results(top_n)

        results = [None] * self.runtimes_result_count
        for module in self.modules:
            rounded = round_runtime(module.runtime)
            start, end = self.runtimes[rounded]
            if end < self.runtimes_result_count:
                results[end] = {
                    module.name: {"precise_runtime": module.runtime, "rounded_runtime": rounded}
                }
                self.runtimes[rounded] = [start, end - 1]
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
        logger.info("counting the modules by rounded runtime")
        self.runtimes = {l: 0 for l in self.runtimes}
        for module in self.modules:
            self.runtimes[round_runtime(module.runtime)] += 1
        logger.info(f"done counting")

    def _count_expected_results(self, top_n: int):
        """
        do prep work - we'll need to know the start/stop indices in the returned results list
        for the runtimes that we care about, and the number of results that we want to return,
        which will top_n, including all ties
        """
        logger.info(
            "prepping expected result count + which indices account for sorted rounded runtime buckets"
        )
        result_count, indices_counted = 0, 0
        for runtime, count in self.runtimes.items():
            if result_count < top_n:
                result_count += count

            self.runtimes[runtime] = [indices_counted, indices_counted + count - 1]
            indices_counted += count
        self.runtimes_result_count = result_count
        logger.info(f"done: will return {result_count} results")


def find_flakiest_modules(module_list: ModuleCollection) -> (float, Dict):
    """
    Wraps the functionality on BubblewrapStats that searches for the flakiest modules
    """
    stats = BubblewrapStats(
        modules=module_list.modules,
        runtimes=module_list.runtimes,
        flakiest_modules=[],
        slowest_modules=[],
    )
    stats.find_flakiest()

    rate = stats.max_flake_rate
    stats = asdict(stats)
    stats = stats.pop("flakiest_modules", None)
    modules = [s["name"] for s in stats]
    return rate, modules


def find_slowest_modules(module_list: ModuleCollection):
    """
    Wraps the functionality on BubblewrapStats for finding the top_n slowest modules
    """
    stats = BubblewrapStats(
        modules=module_list.modules,
        runtimes=module_list.runtimes,
        flakiest_modules=[],
        slowest_modules=[],
    )
    logger.info(
        "calling analyze.find_slowest_modules(execution_results) to find the top 3 or so slow modules"
    )
    return stats.find_slowest(3)
