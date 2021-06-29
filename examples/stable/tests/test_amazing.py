import pytest

from random import randint

from examples.stable.A import amazing
from examples.stable.B import banana


def test_hello():
    assert amazing.hello() == 10
