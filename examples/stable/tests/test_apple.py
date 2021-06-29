import pytest

from examples.stable.A import apple
from examples.stable.A import amazing
from examples.stable.B import blue

import examples.stable.B
import examples.stable.script


def test_hello():
    assert apple.hello() == 10
