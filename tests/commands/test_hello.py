import os
import re

import click
import pytest

from rc3 import cli
from rc3.commands import cmd_request
from rc3.common import json_helper, print_helper


def test_hello_world_times(example_collection, runner):
    result = runner.invoke(cli.cli, ['hello', "--count", "10"])
    assert result.exit_code == 0
    assert result.output.count("Hello World!") == 10


def test_mr(example_collection, runner):
    result = runner.invoke(cli.cli, ['hello', "--mr", "Gary"])
    assert result.exit_code == 0
    assert result.output.count("Mr. Gary!") == 1


def test_title(example_collection, runner):
    result = runner.invoke(cli.cli, ['hello', "--title", "Sir", "Gary"])
    assert result.exit_code == 0
    assert result.output.count("Sir Gary!") == 1
