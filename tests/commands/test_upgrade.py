import os
import re
from pathlib import Path

import click
import pytest

from rc3 import cli
from rc3.commands import cmd_request
from rc3.common import json_helper, print_helper


def global_schema_made_old():
    home = Path.home()
    rc_home = os.path.join(home, ".rc")
    global_fn = os.path.join(rc_home, 'rc-global.json')
    _json = json_helper.read_json(global_fn)

    # update to an older schema $id & write back to filesystem
    _json['$schema'] = "https://json.schemastore.org/rc3-environment-0.0.3.json"
    json_helper.write_json(global_fn, _json)


def test_basic_command_runs(example_collection, runner):
    global_schema_made_old()

    result = runner.invoke(cli.cli, ['upgrade'], input="n\nn\n")
    assert result.exit_code == 0
    assert "Checking RC_HOME schemas... UPGRADES NEEDED" in result.output
    assert "Checking current COLLECTION schemas... OK" in result.output
    assert "COLLECTION REQUEST extract JSON... NOT IMPLEMENTED YET" in result.output
    assert "COLLECTION validating JSON against current schemas... NOT IMPLEMENTED YET" in result.output


def test_upgrade_does_needful(example_collection, runner):
    global_schema_made_old()

    result = runner.invoke(cli.cli, ['upgrade'], input="y\n")
    assert result.exit_code == 0
    assert "Checking RC_HOME schemas... UPGRADES NEEDED" in result.output
    assert "Checking current COLLECTION schemas... OK" in result.output
    assert "COLLECTION REQUEST extract JSON... NOT IMPLEMENTED YET" in result.output
    assert "COLLECTION validating JSON against current schemas... NOT IMPLEMENTED YET" in result.output

    result = runner.invoke(cli.cli, ['upgrade'])
    assert result.exit_code == 0
    assert "Checking RC_HOME schemas... OK" in result.output
    assert "Checking current COLLECTION examples... OK" in result.output
    assert "Checking current COLLECTION schemas... OK" in result.output
