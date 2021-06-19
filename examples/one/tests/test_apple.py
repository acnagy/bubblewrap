import pytest

from A import apple
from A import amazing
from B import blue

import B
import script


def test_hello():
    assert apple.hello() == 10
