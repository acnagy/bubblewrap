"""
invocation for the bubblewrap functionality
"""

import os

from utils import log

logger = log.init_logger()

def bubblewrap(path, trials, prev_commit, fail):
    path = os.path.abspath(path)
    logger.info("Assessing tests for %s", path)
    # collect map of test files + relevant main files on previous commit 
    logger.info("Collecting test files for %s @ %s", path, prev_commit)

    # collect map of test files + relevant main files on current project
    logger.info("Collecting test files for %s @ HEAD", path)

    # more to come.. 

    return