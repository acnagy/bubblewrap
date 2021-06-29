import pytest

from examples.flake.A import awesome

from random import randint


def test_hello():
    assert awesome.hello() == 10


def test_flake():
    value = randint(0, 1)
    assert value == 0
