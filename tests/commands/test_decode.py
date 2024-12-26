import os
import re

import click
import pytest

from rc3 import cli
from rc3.commands import cmd_request
from rc3.common import json_helper, print_helper


def test_decode_default_name(example_collection, oauth2_token, runner):
    # error if no ENV VAR
    result = runner.invoke(cli.cli, ['decode'])
    assert result.exit_code == 1
    assert "No ENV VAR found for" in result.output

    # setup ENV VAR
    fn, env = json_helper.read_environment("current")
    env['token'] = oauth2_token
    json_helper.write_environment(fn, env)

    # execute again, and check results
    result = runner.invoke(cli.cli, ['decode'])
    assert result.exit_code == 0
    assert "Decoding HEADERS and CLAIMS from 'token' env var" in result.output
    assert "kid" in result.output
    assert "alg" in result.output
    assert "sub" in result.output
    assert "Issued at:" in result.output
    assert "Expired at:" in result.output


def test_decode_custom_name(example_collection, oauth2_token, runner):
    # error if no ENV VAR
    result = runner.invoke(cli.cli, ['decode', 'custom'])
    assert result.exit_code == 1
    assert "No ENV VAR found for" in result.output

    # setup ENV VAR
    fn, env = json_helper.read_environment("global")
    env['custom'] = oauth2_token
    json_helper.write_environment(fn, env)

    # default name still fails
    result = runner.invoke(cli.cli, ['decode'])
    assert result.exit_code == 1
    assert "No ENV VAR found for" in result.output

    # custom name, now works
    result = runner.invoke(cli.cli, ['decode', 'custom'])
    assert result.exit_code == 0
    assert "Decoding HEADERS and CLAIMS from 'custom' env var" in result.output
    assert "kid" in result.output
    assert "alg" in result.output
    assert "sub" in result.output
    assert "Issued at:" in result.output
    assert "Expired at:" in result.output


def test_decode_invalid_token(example_collection, oauth2_token, runner):
    # setup ENV VAR
    fn, env = json_helper.read_environment("global")
    env['custom'] = "random crap"
    json_helper.write_environment(fn, env)

    # custom name, now works
    result = runner.invoke(cli.cli, ['decode', 'custom'])
    assert result.exit_code == 1
    assert "There was an error decoding the JWT" in result.output
