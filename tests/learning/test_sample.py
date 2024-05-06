import os

import pytest


# app code
def func(x):
    return x + 1


def f():
    raise SystemExit(1)


# tests
class TestClass:
    def test_answer(self):
        assert func(3) == 4

    def test_mytest(self):
        with pytest.raises(SystemExit):
            f()


def test_answer():
    assert func(4) == 5


def test_mytest(tmp_path):
    print("tmp_path.name")
    print(tmp_path.name)
    print(tmp_path)
    assert tmp_path.exists()
    d = tmp_path / "sub"
    d.mkdir()
    print(d)
    assert d.exists()
