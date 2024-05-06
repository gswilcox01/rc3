import os
import re

import click
import pytest

from rc3 import cli
from rc3.commands import cmd_request
from rc3.common import json_helper, print_helper
from tests.commands import test_request
from tests.util.decorators import activate_responses, activate_recorder


def setup_localhost(runner):
    result = runner.invoke(cli.cli, ['e', '2'])
    assert result.exit_code == 0


def lookup_current():
    wrapper = cmd_request.lookup_request(None)
    r = wrapper.get('_original')
    return r, wrapper


def lookup_current_response():
    r, wrapper = lookup_current()
    response_dir = wrapper.get('_dir')
    response_file = wrapper.get('_filename').split('.')[0] + ".response"
    response_full_file = os.path.join(response_dir, response_file)
    if os.path.exists(response_full_file):
        response = json_helper.read_json(response_full_file)
        return response
    return None


# @activate_recorder()
@activate_responses()
def test_send_1(example_collection, runner):
    setup_localhost(runner)

    result = runner.invoke(cli.cli, ['send'])
    assert result.exit_code == 0
    assert "Hello" in result.output
    assert "English" in result.output

    response = lookup_current_response()
    assert response.get('status_code') == 200


# @activate_recorder()
@activate_responses()
def test_send_basics(example_collection, runner):
    setup_localhost(runner)

    result = runner.invoke(cli.cli, ['r', '--pick', '2'])
    assert result.exit_code == 0
    result = runner.invoke(cli.cli, ['send'])
    assert result.exit_code == 0
    response = lookup_current_response()
    assert response.get('status_code') == 200

    result = runner.invoke(cli.cli, ['r', '--pick', '3'])
    assert result.exit_code == 0
    result = runner.invoke(cli.cli, ['send'])
    assert result.exit_code == 0
    response = lookup_current_response()
    assert response.get('status_code') == 200

    result = runner.invoke(cli.cli, ['r', '--pick', '4'])
    assert result.exit_code == 0
    result = runner.invoke(cli.cli, ['send'])
    assert result.exit_code == 0
    response = lookup_current_response()
    assert response.get('status_code') == 200

    result = runner.invoke(cli.cli, ['r', '--pick', '5'])
    assert result.exit_code == 0
    result = runner.invoke(cli.cli, ['send'])
    assert result.exit_code == 0
    response = lookup_current_response()
    assert response.get('status_code') == 200


def test_var_missing(example_collection, runner):
    setup_localhost(runner)

    result = runner.invoke(cli.cli, ['send', '--pick', '6'])
    assert result.exit_code == 1
    assert "var {{token}} is in the REQUEST but cannot be found" in result.output


# @activate_recorder()
@activate_responses()
def test_mint_extract_use_token(example_collection, runner):
    setup_localhost(runner)

    # pre-test, confirm token doesn't exist/extract works
    result = runner.invoke(cli.cli, ['send', '--pick', '6'])
    assert result.exit_code == 1
    assert "var {{token}} is in the REQUEST but cannot be found" in result.output

    # mint and extract
    result = runner.invoke(cli.cli, ['send', '--pick', 'mint-admin-token'])
    assert result.exit_code == 0
    response = lookup_current_response()
    # NOTE: mint-admin-token, has save_responses=False, so lookup method will return None!
    assert response is None

    # use token
    result = runner.invoke(cli.cli, ['send', '--pick', '6'])
    assert result.exit_code == 0
    response = lookup_current_response()
    assert response.get('status_code') == 200


# @activate_recorder()
@activate_responses()
def test_not_verbose(example_collection, runner):
    setup_localhost(runner)

    result = runner.invoke(cli.cli, ['request', '--pick', '1'])
    assert result.exit_code == 0
    result = runner.invoke(cli.cli, ['send'])
    assert result.exit_code == 0

    response = lookup_current_response()
    assert print_helper.get_json_string(response).strip() not in result.output


# @activate_recorder()
@activate_responses()
def test_is_verbose(example_collection, runner):
    setup_localhost(runner)

    result = runner.invoke(cli.cli, ['request', '--pick', '1'])
    assert result.exit_code == 0
    result = runner.invoke(cli.cli, ['-v', 'send'])
    assert result.exit_code == 0

    response = lookup_current_response()
    assert print_helper.get_json_string(response).strip() in result.output


# @activate_recorder()
@activate_responses()
def test_request_no_responses(runner, example_collection, monkeypatch):
    setup_localhost(runner)

    # Setup global settings WITH responses
    settings = json_helper.read_settings()
    settings['save_responses'] = True
    json_helper.write_settings(settings)

    # Setup request, with no_responses (should override the global settings)
    r, wrapper = lookup_current()
    r['save_responses'] = False
    monkeypatch.setattr(click, "edit", lambda x: print_helper.get_json_string(r))
    # Setup continue, with save to file
    result = runner.invoke(cli.cli, ['r', "--edit"])
    assert result.exit_code == 0
    assert "REQUEST saved" in result.output

    result = runner.invoke(cli.cli, ['send'])
    assert result.exit_code == 0

    # .response file should NOT exist
    response = lookup_current_response()
    assert response is None


# @activate_recorder()
@activate_responses()
def test_settings_no_responses(runner, example_collection, monkeypatch):
    setup_localhost(runner)

    # Setup global settings, with no_responses
    settings = json_helper.read_settings()
    settings['save_responses'] = False
    json_helper.write_settings(settings)

    result = runner.invoke(cli.cli, ['send'])
    assert result.exit_code == 0

    # .response file should NOT exist
    response = lookup_current_response()
    assert response is None


# @activate_recorder()
@activate_responses()
def test_settings_with_responses(runner, example_collection, monkeypatch):
    setup_localhost(runner)

    # Setup global settings
    settings = json_helper.read_settings()
    settings['save_responses'] = True
    json_helper.write_settings(settings)

    result = runner.invoke(cli.cli, ['send'])
    assert result.exit_code == 0

    # .response file SHOULD exist
    response = lookup_current_response()
    assert response is not None
    assert response.get('status_code') == 200



