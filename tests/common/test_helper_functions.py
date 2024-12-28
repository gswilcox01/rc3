import re

import click
import keyring
import pytest
from click import ClickException
from keyring.errors import PasswordDeleteError

from rc3.common import file_helper, helper_functions, env_helper


def test_invalid_helper():
    with pytest.raises(ClickException, match=r'handlebar helper_function \[#unknown\] is invalid!'):
        helper_functions.lookup_helper_value("#unknown")


def test_env_storage(example_collection):
    # Note: example_collection, is used so there is an RC_HOME populated with rc-settings.json

    with pytest.raises(ClickException, match=r'\[elsewhere\] is invalid'):
        helper_functions.lookup_helper_value("#uuid elsewhere.my_uuid")

    u1 = helper_functions.lookup_helper_value("#uuid global.my_uuid")
    env1 = env_helper.lookup_one_var("my_uuid")
    assert u1 == env1

    u2 = helper_functions.lookup_helper_value("#uuid current.my_uuid")
    env2 = env_helper.lookup_one_var("my_uuid")
    assert u2 == env2


def test_pkce_cvcc(example_collection):
    # Note: example_collection, is used so there is an RC_HOME populated with rc-settings.json

    # Negative test
    with pytest.raises(ClickException, match=r'Invalid # of parameters'):
        helper_functions.lookup_helper_value("#pkce_cvcc cv too_many")

    # Positive test
    # Note: CC is returned, CV is stored in environment
    cc = helper_functions.lookup_helper_value("#pkce_cvcc cv")

    # valid characters in oauth2 cc
    pattern = r"^[a-zA-Z0-9\._~-]+$"
    assert re.match(pattern, cc)
    assert len(cc) >= 43
    assert len(cc) <= 128

    # cv has same valid chars
    # cv should always be 128 (default for pkce lib used)
    cv = env_helper.lookup_one_var("cv")
    assert re.match(pattern, cv)
    assert len(cv) == 128

    # Positive test
    # Default env var works
    cc = helper_functions.lookup_helper_value("#pkce_cvcc")
    cv = env_helper.lookup_one_var("code_verifier")
    assert re.match(pattern, cv)
    assert len(cv) == 128


def test_uuid(example_collection):
    # Note: example_collection, is used so there is an RC_HOME populated with rc-settings.json

    # Negative test
    with pytest.raises(ClickException, match=r'Invalid # of parameters'):
        helper_functions.lookup_helper_value("#uuid name too_many")

    # Positive test
    s = helper_functions.lookup_helper_value("#uuid")
    # valid characters in uuid
    pattern = r"^[a-f0-9-]+$"
    assert re.match(pattern, s)
    assert len(s) == 36

    # Positive test + environment storage
    s = helper_functions.lookup_helper_value("#uuid test_uuid")
    s2 = env_helper.lookup_one_var("test_uuid")
    # valid characters in uuid
    pattern = r"^[a-f0-9-]+$"
    assert re.match(pattern, s)
    assert len(s) == 36
    assert s == s2


def test_prompt_helper(example_collection, monkeypatch):
    # Note: example_collection, is used so there is an RC_HOME populated with rc-settings.json

    # Negative test
    with pytest.raises(ClickException, match=r'A prompt is required when using'):
        helper_functions.lookup_helper_value("#prompt")

    # Test with no default
    # mock click.prompt
    def mock_prompt(text, default, hide_input):
        assert text == "What would you like for Christmas?"
        assert default == ""
        assert hide_input is False
        return "toys"
    monkeypatch.setattr(click, 'prompt', mock_prompt)

    s = helper_functions.lookup_helper_value("#prompt What would you like for Christmas?")
    assert s == "toys"

    # Test with default value after ":"
    # mock click.prompt
    def mock_prompt(text, default, hide_input):
        assert text == "What would you like for Christmas?"
        assert default == "Whirled Peas"
        assert hide_input is False
        return "A Pony"
    monkeypatch.setattr(click, 'prompt', mock_prompt)

    s = helper_functions.lookup_helper_value("#prompt What would you like for Christmas?:Whirled Peas")
    assert s == "A Pony"


def test_secure_prompt_helper(example_collection, monkeypatch):
    # Note: example_collection, is used so there is an RC_HOME populated with rc-settings.json

    # Negative test
    with pytest.raises(ClickException, match=r'A prompt is required when using'):
        helper_functions.lookup_helper_value("#secure_prompt")

    # Test with no default
    # mock click.prompt
    def mock_prompt(text, default, hide_input):
        assert text == "What would you like for Christmas?"
        assert default == ""
        assert hide_input is True
        return "toys"
    monkeypatch.setattr(click, 'prompt', mock_prompt)

    s = helper_functions.lookup_helper_value("#secure_prompt What would you like for Christmas?")
    assert s == "toys"


def test_file_helper(example_collection, json_file):
    # Note: example_collection, is used so there is an RC_HOME populated with rc-settings.json

    # Negative test
    with pytest.raises(ClickException, match=r'The #file helper function doesn'):
        helper_functions.lookup_helper_value("#file with_param")

    # Negative test 2
    # Fails because this helper depends on --file option, file_helper to have been called...
    file_helper.reset_for_test()
    with pytest.raises(ClickException, match=r'The --file option must be used since'):
        helper_functions.lookup_helper_value("#file")

    # Positive test
    # file helper will always be called if a file is passed into rc CLI
    file_helper.preprocess_file_option(json_file)
    s = file_helper.consume_as_string()

    # this helper_function (#file) should then always return the contents of that file
    s2 = helper_functions.lookup_helper_value("#file")
    assert "Koar" in s
    assert s == s2


def test_keyring_prompt_helper(example_collection, monkeypatch):
    # Negative test
    with pytest.raises(ClickException, match=r'The #keyring_prompt helper function requires exactly 1 parameter'):
        helper_functions.lookup_helper_value("#keyring_prompt")
    with pytest.raises(ClickException, match=r'The #keyring_prompt helper function requires exactly 1 parameter'):
        helper_functions.lookup_helper_value("#keyring_prompt too many")

    # setup w/ delete in keyring to start
    try:
        keyring.delete_password("rc3", "test_prompt")
    except PasswordDeleteError:
        # just ignore this error if nothing was deleted
        pass
    # setup mock for click.prompt
    def mock_prompt(text, default, hide_input):
        assert text == f"Please enter a value for NAME(test_prompt)"
        assert default is None
        assert hide_input is True
        return "my_secret"
    monkeypatch.setattr(click, 'prompt', mock_prompt)
    before = keyring.get_password("rc3", "test_prompt")

    # execute helper function & click mock
    s = helper_functions.lookup_helper_value("#keyring_prompt test_prompt")
    after = keyring.get_password("rc3", "test_prompt")

    assert before is None
    assert after == "my_secret"
    assert s == "my_secret"


def test_keyring_prompt_no_prompt(example_collection, monkeypatch):
    # setup an existing password in the keyring (prompt shouldn't happen)
    keyring.set_password("rc3", "test_prompt", "hello mom!")
    # setup mock for click.prompt
    def mock_prompt(text, default, hide_input):
        assert False, "prompt shouldn't be called!"
    monkeypatch.setattr(click, 'prompt', mock_prompt)
    before = keyring.get_password("rc3", "test_prompt")

    # execute helper function & click mock
    s = helper_functions.lookup_helper_value("#keyring_prompt test_prompt")
    after = keyring.get_password("rc3", "test_prompt")

    assert before == "hello mom!"
    assert after == "hello mom!"
    assert s == "hello mom!"


def test_keyring_helper(example_collection):
    # Negative test
    with pytest.raises(ClickException, match=r'The #keyring helper function requires exactly 1 parameter'):
        helper_functions.lookup_helper_value("#keyring")
    with pytest.raises(ClickException, match=r'The #keyring helper function requires exactly 1 parameter'):
        helper_functions.lookup_helper_value("#keyring too many")
    with pytest.raises(ClickException, match=r'The #keyring helper function requires the NAME\(.+\) .+ exist'):
        helper_functions.lookup_helper_value("#keyring missing_user")

    keyring.set_password("rc3", "test_name", "test_password")
    s = helper_functions.lookup_helper_value("#keyring test_name")
    assert s == "test_password"

