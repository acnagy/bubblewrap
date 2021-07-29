import hashlib

from math import floor
from dataclasses import dataclass
from typing import Dict, List


"""
Represents an application module and the collected, executed, and summarized unit tests that cover it.
"""


@dataclass
class Module:
    name: str
    trials: int = 0
    flakes: float = 0.0
    total_runtime: float = 0.0
    flake_rate: float = 0.0
    runtime: float = 0.0


"""
Represents a whole executions' worth of modules and the state -- sorted floored runtimes -- that we
need to maintain for our fuzy sort later
"""


@dataclass
class ModuleCollection:
    modules: None  # List[Module]
    runtimes: None  # sorted List of runtimes

    def add(self, module: Module):
        """
        add new module to the list, and insert its floored runtime where appropriate
        """
        self.modules.append(module)
        self._sort_runtime(module)

    def _sort_runtime(self, module: Module):
        """
        sort the runtimes, floored. We'll use this in the analysis phase for returning
        the modules with the slowest tests, including ties
        """
        runtime = floor(module.runtime)
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


def summarize_module_test_results(app_modules_map: Dict, test_results: Dict) -> ModuleCollection:
    """
    Generates a cache of possible test result combos (yes... it's a lot...), then, from looking up the
    actual tests that were run per module, generates and a ModuleCollection of summarized results from
    the real project at hand
    """

    results = test_results["tests"]
    module_collection = ModuleCollection(modules=[], runtimes=[])
    for module_name, tests in app_modules_map.items():
        module = Module(name=module_name)
        for test in tests:
            result_vals = results[test]
            module.trials += result_vals["trials"]
            module.flakes += result_vals["flakes"]
            module.total_runtime += result_vals["runtime_sum"]
        module.flake_rate = module.flakes / module.trials
        module.runtime = module.total_runtime / module.trials
        module_collection.add(module)
    return module_collection


def keyify(test_paths: List[str]) -> bytes:
    """
    creates an md5 hash of a sorted list of test paths to serve as a unique key for test result
    summary combinations.
    """
    test_paths = sorted(test_paths)
    test_paths = "".join(test_paths)
    return hashlib.md5(test_paths.encode("utf-8")).digest()
