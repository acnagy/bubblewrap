import pytest
import os
import sys
import datetime


import script


def test_hello():
    return script.hello() == 100
