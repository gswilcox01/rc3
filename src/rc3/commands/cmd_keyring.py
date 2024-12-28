import json
import os
import click
import keyring

from rc3.commands import cmd_list
from rc3.common import json_helper, print_helper, config_helper, keyring_helper
from rc3.common.data_helper import SCHEMA_BASE_URL, SCHEMA_PREFIX, SCHEMA_VERSION


@click.command("keyring", short_help="Manage passwords in your operating system Keyring/Keychain.")
@click.option('-s', '--set', 'is_set', is_flag=True, default=False, help="Set the VALUE for a NAME in the keyring.")
@click.option('-g', '--get', 'is_get', is_flag=True, default=False, help="Get the VALUE for a NAME in the keyring.")
@click.option('-d', '--del', 'is_delete', is_flag=True, default=False, help="Delete the VALUE for a NAME in the keyring.")
@click.argument('name', type=str, required=True)
def cli(is_set, is_get, is_delete, name):
    """\b
    Manage passwords in your operating system Keyring/Keychain.

    \b
    By default:
    * macOS - Keychain
    * windows - Windows Credential Locker

    """

    # ensure a valid keyring history file, before doing anything
    keyring_history = json_helper.read_keyring()

    if is_get:
        print(keyring_helper.get_value(name))
    elif is_delete:
        keyring_helper.delete_value(name)
    else:
        # --set is default
        prompt = f"Please enter a value for NAME({name})"
        password = click.prompt(prompt, default=None, hide_input=True)
        keyring_helper.set_value(name, password)
