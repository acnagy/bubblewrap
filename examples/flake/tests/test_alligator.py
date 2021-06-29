import pytest

from examples.flake.A import awesome
from examples.flake.A import alligator

from random import randint


def test_hello():
    assert alligator.hello() == 10


def test_flake():
    value = randint(0, 10)
    assert value == 0
