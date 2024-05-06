import os
import re

import pytest

from rc3 import cli
from rc3.common import json_helper, config_helper


def test_init_from_empty(clean_home, clean_empty, runner):
    # pre-test RC_HOME doesn't exist
    rc_home = os.path.join(clean_home, '.rc')
    assert not os.path.exists(rc_home)

    # change to empty dir, and run init
    os.chdir(clean_empty)
    result = runner.invoke(cli.cli, ['init'])
    assert result.exit_code == 0

    # test it exists now AND is empty
    assert os.path.exists(rc_home)
    assert os.listdir(rc_home) == ['global.json', 'schemas', 'settings.json']
    assert os.listdir(clean_empty) == ['collection.json',
                                       'environments',
                                       'examples',
                                       'greetings-basic',
                                       'greetings-oauth2']
    settings = json_helper.read_settings()
    assert settings.get('current_collection') == "c1"


def test_init_from_NOT_empty(clean_home, clean_empty, runner):
    # pre-test RC_HOME doesn't exist
    rc_home = os.path.join(clean_home, '.rc')
    assert not os.path.exists(rc_home)

    # change to empty dir, create tempfile
    # and then run init
    os.chdir(clean_empty)
    json_helper.write_json("temp.json",{})
    result = runner.invoke(cli.cli, ['init'])
    assert result.exit_code == 0

    # test that we DO STILL init RC_HOME
    assert os.path.exists(rc_home)
    assert os.listdir(rc_home) == ['global.json', 'schemas', 'settings.json']
    # BUT we DON'T init the CWD, or import a collection
    assert os.listdir(clean_empty) == ['temp.json']
    settings = json_helper.read_settings()
    assert settings.get('current_collection') == ""

