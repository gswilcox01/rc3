import functools
import inspect
import os

import responses
from responses._recorder import Recorder


def default_filename(func):
    module = inspect.getmodule(func)

    directory = os.path.splitext(module.__file__)[0] + "_files"
    os.makedirs(directory, exist_ok=True)

    filename = func.__name__ + ".yaml"
    return os.path.join(directory, filename)


def activate_responses(file_path=None):
    def inner_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal file_path
            if file_path is None:
                file_path = default_filename(func)

            with responses.RequestsMock() as rsp:
                rsp._add_from_file(file_path=file_path)
                func(*args, **kwargs)

        return wrapper

    return inner_decorator


def activate_recorder(file_path=None):
    def inner_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal file_path
            if file_path is None:
                file_path = default_filename(func)

            recorder = Recorder()
            with recorder:
                result = func(*args, **kwargs)
                recorder.dump_to_file(
                    file_path=file_path, registered=recorder.get_registry().registered
                )
                return result

        return wrapper

    return inner_decorator
