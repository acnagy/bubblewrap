import pytest

from B import banana
from B import blue
from A import amazing


def test_hello():
    assert banana.hello() == 10
