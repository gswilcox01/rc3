import os

import pytest

from rc3 import cli


def test_first_run_help(runner):
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    assert "Usage" in result.output
    assert "Show this message and exit" in result.output


def test_any_command_creates_initialized_rc_home(clean_home, runner):
    # pre-test it doesn't exist from a pytest fixture
    rc_home = os.path.join(clean_home, '.rc')
    assert not os.path.exists(rc_home)

    # hello cmd doesn't matter, we just need some cmd some cli.cli is invoked instead of help displayed
    result = runner.invoke(cli.cli, ['hello'])
    assert result.exit_code == 0
    assert "Hello" in result.output

    # test it exists now AND is empty
    assert os.path.exists(rc_home)
    assert len(os.listdir(rc_home)) == 3


def test_shortcuts_work(example_collection, runner):
    result = runner.invoke(cli.cli, ['r', '--list'])
    assert result.exit_code == 0
    assert "Listing REQUESTS" in result.output
    result2 = runner.invoke(cli.cli, ['request', '--list'])
    assert result2.exit_code == 0
    assert result.output == result2.output

    result = runner.invoke(cli.cli, ['c', '--list'])
    assert result.exit_code == 0
    assert "Listing COLLECTIONS" in result.output
    result2 = runner.invoke(cli.cli, ['collection', '--list'])
    assert result2.exit_code == 0
    assert result.output == result2.output

    result = runner.invoke(cli.cli, ['e', '--list'])
    assert result.exit_code == 0
    assert "Listing ENVIRONMENTS" in result.output
    result2 = runner.invoke(cli.cli, ['environment', '--list'])
    assert result2.exit_code == 0
    assert result.output == result2.output
