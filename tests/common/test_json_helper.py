import os
from json import JSONDecodeError
from pathlib import Path

import pytest
from click import ClickException

from rc3.common import file_helper, json_helper


def test_missing_file(example_collection):
    with pytest.raises(ClickException, match=r'Can\'t find: missing.json'):
        _dict = json_helper.load_and_validate("missing.json")


def test_malformed_json(bad_json_file):
    with pytest.raises(ClickException, match=r'unable to load file as JSON'):
        filename = bad_json_file.name
        _dict = json_helper.load_and_validate(filename)


def test_schema_failure(bad_request_file, capsys):
    with pytest.raises(SystemExit):
        filename = bad_request_file.name
        _dict = json_helper.load_and_validate(filename)
    captured = capsys.readouterr()
    assert "Error: file doesn't pass JSON schema validation" in captured.out
    assert " * json path: /method" in captured.out
    assert " * error: 'G' is not one of ['GET'" in captured.out


def test_read_or_none(bad_json_file, bad_request_file):
    # invalid JSON file, returns None
    filename = bad_json_file.name
    r = json_helper.read_json_or_none(filename)
    assert r is None

    # create path to missing file (in same directory)
    directory = os.path.dirname(bad_json_file)
    filename = Path(directory) / "missing.json"
    assert filename.exists() is False
    r = json_helper.read_json_or_none(filename)
    assert r is None

    # reads json (no schema testing)
    filename = bad_request_file.name
    _dict = json_helper.read_json_or_none(filename)
    assert _dict['method'] == "G"
