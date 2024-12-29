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
@click.option('-l', '--list', '_list', is_flag=True, default=False, help="List keyring history.")
@click.argument('name', type=str, required=False)
def cli(is_set, is_get, is_delete, _list, name):
    """\b
    Manage passwords in your operating system Keyring/Keychain.

    \b
    By default:
    * macOS - Keychain
    * windows - Windows Credential Locker

    """

    # allows argument to be a name or # from the list
    entry = lookup_entry(name)
    if entry is not None:
        name = entry['name']

    if _list:
        list_keyring_entries()
    elif is_set:
        prompt = f"Please enter a value for NAME({name})"
        password = click.prompt(prompt, default=None, hide_input=True)
        keyring_helper.set_value(name, password)
    elif is_get:
        print(keyring_helper.get_value(name))
    elif is_delete:
        keyring_helper.delete_value(name)
    elif name is not None:
        # default is --get if name passed
        print(keyring_helper.get_value(name))
    else:
        # otherwise default is --list
        list_keyring_entries()


def lookup_entry(name):
    _list = json_helper.read_keyring_entry_list()

    for entry in _list:
        if name is not None and name == entry.get('name', None):
            return entry
        if name is not None and name == str(entry.get('number', 0)):
            return entry
    return None


def list_keyring_entries():
    _list = json_helper.read_keyring_entry_list()

    if len(_list) == 0:
        raise click.ClickException("No KEYRING history found in settings")
    click.echo("Listing KEYRING history:")

    # now display table
    header = ['NUM:', 'NAME:', 'MODIFIED:', 'ACCESSED:']
    fields = ['display_num', 'name', 'display_modified', 'display_accessed']
    print_helper.print_formatted_table(header, fields, _list)


