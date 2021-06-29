import pytest
import os
import sys
import datetime


import examples.stable.script as script


def test_hello():
    return script.hello() == 100
