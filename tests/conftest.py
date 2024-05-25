import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from rc3 import cli


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
def clean_rc(clean_home, monkeypatch):
    rc_home = os.path.join(clean_home, '.rc')
    os.mkdir(rc_home)
    monkeypatch.setenv('RC_HOME', rc_home)
    yield rc_home


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
