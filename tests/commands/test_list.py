import os
import re

import pytest

from rc3 import cli
from rc3.common import json_helper


def test_initial_list(example_collection, runner):
    result = runner.invoke(cli.cli, ['list'])
    assert result.exit_code == 0

    assert "Listing COLLECTIONS" in result.output
    assert "Listing ENVIRONMENTS" in result.output
    assert "Listing REQUESTS" in result.output
    assert len(re.findall(r'1\*', result.output)) == 3


def test_collections_only(example_collection, runner):
    result = runner.invoke(cli.cli, ['list', 'collections'])
    assert result.exit_code == 0

    assert "Listing COLLECTIONS" in result.output
    assert "Listing ENVIRONMENTS" not in result.output
    assert "Listing REQUESTS" not in result.output
    assert len(re.findall(r'1\*', result.output)) == 1
    out1 = result.output

    # just a 'c' is needed
    result = runner.invoke(cli.cli, ['list', 'c'])
    assert result.output == out1

    # anything after the 'c' doesn't matter
    result = runner.invoke(cli.cli, ['list', 'calamity'])
    assert result.output == out1


def test_environment_only(example_collection, runner):
    result = runner.invoke(cli.cli, ['list', 'environments'])
    assert result.exit_code == 0

    assert "Listing COLLECTIONS" not in result.output
    assert "Listing ENVIRONMENTS" in result.output
    assert "Listing REQUESTS" not in result.output
    assert len(re.findall(r'1\*', result.output)) == 1
    out1 = result.output

    # just a 'e' is needed
    result = runner.invoke(cli.cli, ['list', 'e'])
    assert result.output == out1

    # anything after the 'e' doesn't matter
    result = runner.invoke(cli.cli, ['list', 'elephants'])
    assert result.output == out1


def test_requests_only(example_collection, runner):
    result = runner.invoke(cli.cli, ['list', 'requests'])
    assert result.exit_code == 0

    assert "Listing COLLECTIONS" not in result.output
    assert "Listing ENVIRONMENTS" not in result.output
    assert "Listing REQUESTS" in result.output
    assert len(re.findall(r'1\*', result.output)) == 1
    out1 = result.output

    # just a 'r' is needed
    result = runner.invoke(cli.cli, ['list', 'r'])
    assert result.output == out1

    # anything after the 'r' doesn't matter
    result = runner.invoke(cli.cli, ['list', 'rhinoceros'])
    assert result.output == out1
