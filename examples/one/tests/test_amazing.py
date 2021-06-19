import pytest

from A import amazing
from B import banana


def test_hello():
    assert amazing.hello() == 10
