import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from rc3 import cli
from rc3.common import json_helper


@pytest.fixture(scope="function")
def runner(request):
    return CliRunner()


@pytest.fixture(scope="function")
def clean_home(tmp_path, monkeypatch, autouse=True):
    home = tmp_path
    os.chdir(home)
    monkeypatch.setenv('RC_NO_CACHE', "True")
    monkeypatch.setenv('HOME', str(home))
    monkeypatch.setattr(Path, "home", lambda: Path(home))
    monkeypatch.setattr(os.path, 'expanduser', lambda u: home)
    yield home


@pytest.fixture(scope="function")
def yes_cache(monkeypatch):
    monkeypatch.setenv('RC_NO_CACHE', "False")
    yield "True"


@pytest.fixture(scope="function")
def yes_durations(monkeypatch):
    monkeypatch.setenv('RC_DURATIONS', "True")
    yield "True"


@pytest.fixture(scope="function")
def no_durations(monkeypatch):
    monkeypatch.setenv('RC_DURATIONS', "False")
    yield "False"


# @pytest.fixture(scope="function")
# def clean_rc(clean_home, monkeypatch):
#     rc_home = os.path.join(clean_home, '.rc')
#     os.mkdir(rc_home)
#     monkeypatch.setenv('RC_HOME', rc_home)
#     yield rc_home


@pytest.fixture(scope="function", autouse=True)
def clean_empty(clean_home):
    empty_dir = os.path.join(clean_home, 'empty')
    os.mkdir(empty_dir)
    yield empty_dir


@pytest.fixture(scope="function")
def example_collection(clean_empty, runner):
    os.chdir(clean_empty)
    result = runner.invoke(cli.cli, ['new'], input='example-collection\n\n')
    assert result.exit_code == 0
    yield clean_empty


@pytest.fixture
def text_file(tmp_path):
    file_path = tmp_path / "my.txt"
    file_path.write_text("Hello, World!")
    return file_path


@pytest.fixture
def missing_file(tmp_path):
    file_path = tmp_path / "missing.txt"
    return file_path


@pytest.fixture
def json_file(tmp_path):
    file_path = tmp_path / "my.json"
    with open(file_path, 'w') as fh:
        json.dump({
            "text": "Koar",
            "language": "Martian"
        }, fh)
    return file_path


@pytest.fixture
def json_english_file(tmp_path):
    file_path = tmp_path / "my_english.json"
    with open(file_path, 'w') as fh:
        json.dump({
            "text": "Hello",
            "language": "English"
        }, fh)
    return file_path


@pytest.fixture
def bad_json_file(example_collection):
    file_path = Path(example_collection) / "bad.request"
    # bad json, no schema attribute, no opening brace
    file_path.write_text('"method": "GET",\n"url": "{{baseUrl}}/v1/greetings/1"\n}"')
    return file_path


@pytest.fixture
def bad_request_file(example_collection):
    file_path = Path(example_collection) / "bad_structure.request"
    with open(file_path, 'w') as fh:
        # "G" is not a valid method
        json.dump({
            "$schema": "https://cdn.statically.io/gh/gswilcox01/rc3/v0.0.8/src/rc3/data/schemas/rc3-request-0.0.8.json",
            "method": "G",
            "url": "{{baseUrl}}/v1/greetings/1"
        }, fh)
    return file_path


@pytest.fixture
def oauth2_token():
    yield "eyJraWQiOiI0OWU4MDk4ZC05MThlLTRiOGQtODhjZi1iYTI1MWEwNjhlYTAiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJncmVldGluZ3MtYWRtaW4iLCJhdWQiOiJncmVldGluZ3MtYWRtaW4iLCJuYmYiOjE3MTgzOTc2NTYsInNjb3BlIjpbImdyZWV0aW5ncy53cml0ZSJdLCJpc3MiOiJodHRwOi8vZ3JlZXRpbmdzLW12cnN5Z28zZ3EtdWMuYS5ydW4uYXBwIiwiZXhwIjoxNzE4NDAxMjU2LCJpYXQiOjE3MTgzOTc2NTYsImp0aSI6IjZlNGRmMTQ0LTVmNGEtNGQ0Ny04ZjdiLWRjMTYwZTQxMzU2MCJ9.SXT-OFJu4C2tE-3w1lEJ8Cfil7NMjUFfX7Wx48poHbhpJU31ybR_0R3c9WPd76Fjgw6jXFaK02E0NOsx8D2UsMo1UI1H_OrKWyq7qbthyl_txmpAAzNAhJhS52lXd9hZGrb9Gz_U_dM-vC0K0UqOqihbVvSOzqqX4ROdiNsDW73jasnQlE8TbMCxc1kfKRAdic5-rCPPl-ZzyrOm89AprWd8urDa2urhsGCJDrVLD_FB2yQ1aHvySa1FTvq7kjdLrge9tpFSQp1YW6W3O6gqmmDabj7ZYWyVFcsaflKQZk-gdDvb6KjaappwIiUZq_Ut4RHHXeDHolwY3WVwNoMnkg"

