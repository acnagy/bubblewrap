from examples.flake.A import alligator

from random import randint


def hello():
    print("hello from awesome!")
    return 10


def test_flake():
    value = randint(0, 1)
    assert value == 1
