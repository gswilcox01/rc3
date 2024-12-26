import json
import os
import re
from pathlib import Path

import click
import pytest
import requests
from requests.exceptions import SSLError

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


def test_only_one_body(example_collection, runner):
    # WARNING, this test is behaving weird, and most come first...
    # setup editing of request 3
    _json = {
        "$schema": "https://cdn.statically.io/gh/gswilcox01/rc3/v0.0.8/src/rc3/data/schemas/rc3-request-0.0.8.json",
        "method": "POST",
        "url": "{{baseUrl}}/v1/greetings",
        "auth": {
            "type": "inherit"
        },
        "body": {
            "json": {
                "text": "Koar",
                "language": "Martian"
            },
            "text": "Hello World!"
        }
    }
    file_path = Path(example_collection) / "greetings-basic" / "bad-greetings.request"
    with open(file_path, 'w') as fh:
        json.dump(_json, fh)

    # execute
    result = runner.invoke(cli.cli, ['send', 'bad-greetings'])
    assert result.exit_code == 1
    assert 'REQUEST can only have 1 of body' in result.output


# @activate_recorder()
@activate_responses()
def test_text_with_custom_header(example_collection, runner):
    _json = {
        "$schema": "https://cdn.statically.io/gh/gswilcox01/rc3/v0.0.8/src/rc3/data/schemas/rc3-request-0.0.8.json",
        "method": "POST",
        "url": "{{baseUrl}}/v1/greetings",
        "auth": {
            "type": "inherit"
        },
        "body": {
            "text": "{\"text\": \"Koar\", \"language\": \"Martian\"}"
        }
    }
    file_path = Path(example_collection) / "greetings-basic" / "custom-header.request"
    with open(file_path, 'w') as fh:
        json.dump(_json, fh)

    # execute
    # NOTE: if "body.text" is used, then Content-Type = "text/plain"
    result = runner.invoke(cli.cli, ['send', 'custom-header'])
    assert result.exit_code == 0
    assert 'Unsupported Media Type' in result.output

    # UNLESS!
    # a custom header is set in the request
    _json = {
        "$schema": "https://cdn.statically.io/gh/gswilcox01/rc3/v0.0.8/src/rc3/data/schemas/rc3-request-0.0.8.json",
        "method": "POST",
        "url": "{{baseUrl}}/v1/greetings",
        "headers": {
            "Content-Type": "application/json"
        },
        "auth": {
            "type": "inherit"
        },
        "body": {
            "text": "{\"text\": \"Koar\", \"language\": \"Martian\"}"
        }
    }
    file_path = Path(example_collection) / "greetings-basic" / "custom-header2.request"
    with open(file_path, 'w') as fh:
        json.dump(_json, fh)

    # execute
    result = runner.invoke(cli.cli, ['send', 'custom-header2'])
    assert result.exit_code == 0
    assert 'Koar' in result.output
    assert 'Martian' in result.output


# @activate_recorder()
@activate_responses()
def test_invalid_when_multiple(example_collection, runner, text_file):
    setup_localhost(runner)

    # first just test multiple "names" works
    result = runner.invoke(cli.cli, ['send', '1', '1', '1'])
    assert result.exit_code == 0
    assert result.output.count("Hello") == 3
    assert result.output.count("English") == 3

    # then test each invalid option when multiple
    result = runner.invoke(cli.cli, ['send', '--pick', '1', '1', '1'])
    assert result.exit_code == 1
    assert "invalid if multiple REQUEST_NAMES" in result.output
    result = runner.invoke(cli.cli, ['send', '--edit', '1', '1', '1'])
    assert result.exit_code == 1
    assert "invalid if multiple REQUEST_NAMES" in result.output
    result = runner.invoke(cli.cli, ['send', '--file', text_file, '1', '1', '1'])
    assert result.exit_code == 1
    assert "invalid if multiple REQUEST_NAMES" in result.output


# @activate_recorder()
@activate_responses()
def test_pick_and_edit(example_collection, runner, monkeypatch):
    setup_localhost(runner)

    # first just send request 1 and confirm results
    result = runner.invoke(cli.cli, ['send', '1'])
    assert result.exit_code == 0
    assert '"id": 1' in result.output
    assert "Hello" in result.output
    assert "English" in result.output

    # setup editing of request 1
    result = runner.invoke(cli.cli, ['request', '--info', '1'])
    json_string = print_helper.extract_json_string(result.output)
    json_string = json_string.replace("greetings/1", "greetings/2")
    assert json_string.count("greetings/2") == 1
    monkeypatch.setattr(click, "edit", lambda x: json_string)

    # execute with monkeypatched click.edit
    result = runner.invoke(cli.cli, ['send', '--pick', '1', '--edit'])
    assert result.exit_code == 0
    assert '"id": 2' in result.output
    assert "Hola" in result.output
    assert "Spanish" in result.output


# @activate_recorder()
@activate_responses()
def test_edit(example_collection, runner, monkeypatch):
    setup_localhost(runner)

    # first just send request 1 and confirm results
    result = runner.invoke(cli.cli, ['send'])
    assert result.exit_code == 0
    assert '"id": 1' in result.output
    assert "Hello" in result.output
    assert "English" in result.output

    # setup editing of request 1
    result = runner.invoke(cli.cli, ['request', '--info', '1'])
    json_string = print_helper.extract_json_string(result.output)
    json_string = json_string.replace("greetings/1", "greetings/2")
    assert json_string.count("greetings/2") == 1
    monkeypatch.setattr(click, "edit", lambda x: json_string)

    # execute with monkeypatched click.edit
    result = runner.invoke(cli.cli, ['send', '--edit', '1'])
    assert result.exit_code == 0
    assert '"id": 2' in result.output
    assert "Hola" in result.output
    assert "Spanish" in result.output


# @activate_recorder()
@activate_responses()
def test_lookup_and_send(example_collection, runner, monkeypatch):
    setup_localhost(runner)

    # simple
    result = runner.invoke(cli.cli, ['r', '--send', '2'])
    assert result.exit_code == 0
    assert '"id": 2' in result.output
    assert "Hola" in result.output
    assert "Spanish" in result.output

    # failure
    result = runner.invoke(cli.cli, ['r', '--send', '999'])
    assert result.exit_code == 1
    assert "REQUEST '999' not found" in result.output


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
def test_extract_stdout(example_collection, runner):
    _json = {
        "$schema": "https://cdn.statically.io/gh/gswilcox01/rc3/v0.0.8/src/rc3/data/schemas/rc3-request-0.0.8.json",
        "method": "POST",
        "url": "{{baseUrl}}/v1/greetings",
        "auth": {
            "type": "inherit"
        },
        "body": {
            "json": {
                "text": "Koar",
                "language": "Martian"
            }
        },
        "extract": [
            {
                "json_path": "$.text",
                "to": "stdout"
            }
        ]
    }
    file_path = Path(example_collection) / "greetings-basic" / "extract-stdout.request"
    with open(file_path, 'w') as fh:
        json.dump(_json, fh)

    # execute
    result = runner.invoke(cli.cli, ['send', 'extract-stdout'])
    assert result.exit_code == 0
    assert 'Koar' in result.output
    assert 'text' not in result.output
    assert 'Martian' not in result.output


# @activate_recorder()
@activate_responses()
def test_extract_to_response(example_collection, runner):
    _json = {
        "$schema": "https://cdn.statically.io/gh/gswilcox01/rc3/v0.0.8/src/rc3/data/schemas/rc3-request-0.0.8.json",
        "method": "POST",
        "url": "{{baseUrl}}/v1/greetings",
        "auth": {
            "type": "inherit"
        },
        "body": {
            "json": {
                "text": "Koar",
                "language": "Martian"
            }
        },
        "extract": [
            {
                "text_pattern": "text\\\".\\\"(.*?)\\\"",
                "to": "response",
                "var": "extracted_text"
            }
        ]
    }
    file_path = Path(example_collection) / "greetings-basic" / "extract-response.request"
    with open(file_path, 'w') as fh:
        json.dump(_json, fh)

    # execute
    result = runner.invoke(cli.cli, ['send', '--pick', 'extract-response'])
    assert result.exit_code == 0
    response = lookup_current_response()
    print(response)
    assert len(response['extract_errors']) == 0
    assert response['extracted']['extracted_text'] == "Koar"


# @activate_recorder()
@activate_responses()
def test_extract_regex_errors(example_collection, runner):
    _json = {
        "$schema": "https://cdn.statically.io/gh/gswilcox01/rc3/v0.0.8/src/rc3/data/schemas/rc3-request-0.0.8.json",
        "method": "POST",
        "url": "{{baseUrl}}/v1/greetings",
        "auth": {
            "type": "inherit"
        },
        "body": {
            "json": {
                "text": "Koar",
                "language": "Martian"
            }
        },
        "extract": [
            {
                "text_pattern": "text\\\".\\\".*?\\\"",
                "to": "response",
                "var": "extracted_text"
            }
        ]
    }
    file_path = Path(example_collection) / "greetings-basic" / "extract-errors.request"
    with open(file_path, 'w') as fh:
        json.dump(_json, fh)

    # execute
    result = runner.invoke(cli.cli, ['send', '--pick', 'extract-errors'])
    assert result.exit_code == 0
    response = lookup_current_response()
    print(response)
    assert len(response['extract_errors']) == 1
    assert "MUST contain a matching group" in response['extract_errors'][0]
    assert response['extracted']['extracted_text'] is None

    # again, with different error
    _json['extract'][0]['text_pattern'] = "garbage(.*?)garbage"
    file_path = Path(example_collection) / "greetings-basic" / "extract-errors2.request"
    with open(file_path, 'w') as fh:
        json.dump(_json, fh)

    # execute
    result = runner.invoke(cli.cli, ['send', '--pick', 'extract-errors2'])
    assert result.exit_code == 0
    response = lookup_current_response()
    print(response)
    assert len(response['extract_errors']) == 1
    assert "had no matches in response JSON" in response['extract_errors'][0]
    assert response['extracted']['extracted_text'] is None


# @activate_recorder()
@activate_responses()
def test_extract_garbage(example_collection, runner):
    _json = {
        "$schema": "https://cdn.statically.io/gh/gswilcox01/rc3/v0.0.8/src/rc3/data/schemas/rc3-request-0.0.8.json",
        "method": "POST",
        "url": "{{baseUrl}}/v1/greetings",
        "auth": {
            "type": "inherit"
        },
        "body": {
            "json": {
                "text": "Koar",
                "language": "Martian"
            }
        },
        "extract": [
            {
                "json_path": "$.text",
                "to": "garbage",
                "var": "never"
            }
        ]
    }
    file_path = Path(example_collection) / "greetings-basic" / "extract-garbage.request"
    with open(file_path, 'w') as fh:
        json.dump(_json, fh)

    # execute
    result = runner.invoke(cli.cli, ['send', 'extract-garbage'])
    assert result.exit_code == 0
    assert "Error: file doesn't pass JSON schema validation" in result.output


# @activate_recorder()
@activate_responses()
def test_extract_jsonpath_error(example_collection, runner):
    _json = {
        "$schema": "https://cdn.statically.io/gh/gswilcox01/rc3/v0.0.8/src/rc3/data/schemas/rc3-request-0.0.8.json",
        "method": "GET",
        "url": "{{baseUrl}}/v3/greetings/1",
        "auth": {
            "type": "bearer",
            "bearer_token": "missing"
        },
        "extract": [
            {
                "json_path": "$.text",
                "to": "global",
                "var": "somevar"
            }
        ]
    }
    file_path = Path(example_collection) / "greetings-basic" / "extract-json-error.request"
    with open(file_path, 'w') as fh:
        json.dump(_json, fh)

    # execute
    result = runner.invoke(cli.cli, ['send', '--pick', 'extract-json-error'])
    assert result.exit_code == 0
    response = lookup_current_response()
    print(response)
    assert len(response['extract_errors']) == 1
    assert "but response is not JSON" in response['extract_errors'][0]


# @activate_recorder()
@activate_responses()
def test_extract_jsonpath_error2(example_collection, runner):
    _json = {
        "$schema": "https://cdn.statically.io/gh/gswilcox01/rc3/v0.0.8/src/rc3/data/schemas/rc3-request-0.0.8.json",
        "method": "POST",
        "url": "{{baseUrl}}/v1/greetings",
        "auth": {
            "type": "inherit"
        },
        "body": {
            "json": {
                "text": "Koar",
                "language": "Martian"
            }
        },
        "extract": [
            {
                "json_path": "$.garbage",
                "to": "global",
                "var": "somevar"
            }
        ]
    }
    file_path = Path(example_collection) / "greetings-basic" / "extract-json-error2.request"
    with open(file_path, 'w') as fh:
        json.dump(_json, fh)

    # execute
    result = runner.invoke(cli.cli, ['send', '--pick', 'extract-json-error2'])
    assert result.exit_code == 0
    assert "Koar" in result.output
    assert "Martian" in result.output
    response = lookup_current_response()
    print(response)
    assert len(response['extract_errors']) == 1
    assert "had no matches in response JSON!" in response['extract_errors'][0]


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


# @activate_recorder()
@activate_responses()
def test_send_file(example_collection, runner, json_english_file):
    setup_localhost(runner)

    # first just send request 3 (no file), and confirm output
    result = runner.invoke(cli.cli, ['send', '3'])
    assert result.exit_code == 0
    assert '"id": 6' in result.output
    assert "Koar" in result.output
    assert "Martian" in result.output

    # next send a file with request 3, and expect NOT Koar/Martian
    result = runner.invoke(cli.cli, ['send', '--file', json_english_file, '3'])
    assert result.exit_code == 0
    assert '"id": 7' in result.output
    assert "Hello" in result.output
    assert "English" in result.output

    # next mimic using STDIN to send a file with request 3, and expect NOT Koar/Martian
    result = runner.invoke(cli.cli, ['send', '--file', '-', '3'], input='{ "text": "Hello", "language": "English"}')
    assert result.exit_code == 0
    assert '"id": 8' in result.output
    assert "Hello" in result.output
    assert "English" in result.output


# @activate_recorder()
@activate_responses()
def test_invalid_ca_bundle(example_collection, runner, text_file, missing_file):
    # setup 1: some random file that exists (not actually a ca bundle...)
    setup_localhost(runner)
    settings = json_helper.read_settings()
    settings['ca_bundle'] = str(text_file)
    json_helper.write_settings(settings)

    # first, no error if ca_bundle file exists...
    result = runner.invoke(cli.cli, ['send', '1'])
    assert result.exit_code == 0
    assert result.output.count("Hello") == 1
    assert result.output.count("English") == 1

    # setup 2: a path to a missing file...
    setup_localhost(runner)
    settings = json_helper.read_settings()
    settings['ca_bundle'] = str(missing_file)
    json_helper.write_settings(settings)

    # second, no error if ca_bundle file exists...
    result = runner.invoke(cli.cli, ['send', '1'])
    assert result.exit_code == 1
    assert "Error: settings.json ca_bundle file" in result.output


# @activate_recorder()
@activate_responses()
def test_mock_ca_error(example_collection, runner, monkeypatch):
    # setup_localhost(runner)
    # setup
    def raise_ssl_error(*args, **kwargs):
        raise SSLError("mock error message")
    monkeypatch.setattr(requests, "request", raise_ssl_error)

    # first, no error if ca_bundle file exists...
    result = runner.invoke(cli.cli, ['send', '1'])
    assert result.exit_code == 1
    assert "SSLError: mock error message" in result.output
    assert "Try setting REQUESTS_CA_BUNDLE, CURL_CA_BUNDLE" in result.output

