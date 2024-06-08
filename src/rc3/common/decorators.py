import collections
import collections.abc
import os

from funcy import print_durations, decorator

collections.Hashable = collections.abc.Hashable


@decorator
def rc_print_durations(call):
    rc_durations = os.getenv("RC_DURATIONS", 'False').lower() in ('true', '1')
    if not rc_durations:
        return call()

    with print_durations(call._func.__name__, unit="ms"):
        return call()


super_cache={}
@decorator
def rc_memoized(call):
    func_name = call._func.__name__
    args = call._args
    no_cache = os.getenv("RC_NO_CACHE", 'False').lower() in ('true', '1')
    if no_cache:
        return call()
    if not isinstance(args, collections.Hashable):
        return call()

    my_cache = super_cache.get(func_name)
    if my_cache is None:
        my_cache = super_cache[func_name] = {}

    if args in my_cache:
        # print(f'cached func_name=[{func_name}], cached=True')
        return my_cache[args]
    else:
        # print(f'cached func_name=[{func_name}], cached=False')
        my_cache[args] = call()
        return my_cache[args]


def rc_clear_cache(func_name):
    super_cache[func_name] = {}