import pytest

from examples.stable.B import banana
from examples.stable.B import blue
from examples.stable.A import amazing


def test_hello():
    assert banana.hello() == 10
