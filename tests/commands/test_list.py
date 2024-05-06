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
