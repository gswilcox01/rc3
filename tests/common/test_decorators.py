from datetime import datetime
import time

from rc3.common.decorators import rc_memoized, rc_clear_cache, rc_print_durations


# import rc3.common.decorators as deco


@rc_memoized
def memoized_function(key):
    now = datetime.now()
    return {
        "date": now.strftime("%m/%d/%Y, %H:%M:%S.%f")
    }


@rc_memoized
def memoized_not_hashable_function(_list):
    now = datetime.now()
    return {
        "date": now.strftime("%m/%d/%Y, %H:%M:%S.%f")
    }

@rc_print_durations
def durations_function():
    time.sleep(.1)
    now = datetime.now()
    return {
        "date": now.strftime("%m/%d/%Y, %H:%M:%S.%f")
    }


def test_memoized_works(yes_cache):
    r1 = memoized_function("test")
    time.sleep(.5)
    r2 = memoized_function("test")

    assert r1["date"] == r2["date"]


def test_diffkeys_diffresults(yes_cache):
    r1 = memoized_function("test1")
    time.sleep(.5)
    r2 = memoized_function("test2")

    assert r1["date"] != r2["date"]


def test_disabling_cache(yes_cache, monkeypatch):
    # override yes_cache for this 1 test, explicitly
    monkeypatch.setenv('RC_NO_CACHE', "True")

    r1 = memoized_function("test")
    time.sleep(.5)
    r2 = memoized_function("test")

    assert r1["date"] != r2["date"]


def test_clearing_cache(yes_cache):
    r1 = memoized_function("test")
    time.sleep(.5)
    rc_clear_cache("memoized_function")
    r2 = memoized_function("test")

    # when we clear cache, results will be different even for the same key/arg
    assert r1["date"] != r2["date"]


def test_not_hashable_doesnt_barf(yes_cache):
    r1 = memoized_not_hashable_function([1, 2, 3])
    time.sleep(.5)
    r2 = memoized_not_hashable_function([1, 2, 3])

    # lists are not hashable in python
    # test that no error, we just silently DO NOT cache this function
    assert r1["date"] != r2["date"]


def test_durations_printed(yes_durations, capsys):
    durations_function()
    durations_function()
    durations_function()
    captured = capsys.readouterr()

    assert captured.out.count("ms in durations_function") == 3


def test_durations_disabled(yes_durations, monkeypatch, capsys):
    # override yes_durations for this 1 test, explicitly
    monkeypatch.setenv('RC_DURATIONS', "False")

    durations_function()
    durations_function()
    durations_function()
    captured = capsys.readouterr()

    # if disabled, no "ms in <func>" should be printed
    assert captured.out.count("ms in durations_function") == 0




