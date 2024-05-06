import json
import os
import click

from rc3.commands import cmd_list
from rc3.common import json_helper, print_helper
from rc3.common.data_helper import COLLECTION_FILENAME


@click.command("collection", short_help="Manage COLLECTIONS defined in settings.")
@click.option('-l', '--list', '_list', is_flag=True, default=False, help="List COLLECTIONS in settings.")
@click.option('-i', '--info', is_flag=True, default=False, help="Display json of current COLLECTION.")
@click.option('-p', '--pick', is_flag=True, default=False, help="Pick an item as current COLLECTION.")
@click.option('-e', '--edit', is_flag=True, default=False, help="Edit a COLLECTION with system editor.")
@click.argument('collection_name', type=str, required=False)
def cli(_list, info, pick, edit, collection_name):
    """\b
    Manages COLLECTIONS that have been imported into settings.json.

    \b
    COLLECTION_NAME is optional.
    COLLECTION_NAME will default to the current_collection, or prompt you to pick.
    COLLECTION_NAME if used should be one of:
    1. The NUM column from 'rc collection --list' output
    2. THe NAME column from 'rc collection --list' output

    """
    if _list:
        cmd_list.list_collections()
    elif edit:
        click.echo("NOT IMPLEMENTED! Please use VSCode to edit your collection.")
    elif info:
        print_info(collection_name)
    elif pick:
        pick_collection(collection_name)
    elif collection_name is None:
        # DEFAULT to list() if no COLLECTION_NAME
        cmd_list.list_collections()
    else:
        # DEFAULT to pick() if COLLECTION_NAME
        pick_collection(collection_name)


def pick_collection(name=None):
    c = lookup_or_prompt(name)
    if c is None:
        return None

    settings = json_helper.read_settings()
    settings['current_collection'] = c['name']
    json_helper.write_settings(settings)

    click.echo("COLLECTION has been picked: " + c['name'])
    return c


def lookup_or_prompt(name, prompt="Which COLLECTION do you want to pick?"):
    _list = json_helper.read_collection_list()
    if len(_list) == 0:
        raise click.ClickException("Invalid option.  There are no COLLECTIONS defined.")

    picked_object = None
    if name is None:
        cmd_list.list_collections()
        current_c = lookup_collection(None)
        default_choice = 0 if current_c is None else current_c.get('number', 0)
        number = click.prompt(prompt, default=default_choice)
        picked_object = lookup_collection(str(number))
        if picked_object is None:
            raise click.ClickException("Invalid selection")
    else:
        picked_object = lookup_collection(name)
        if picked_object is None:
            raise click.ClickException("COLLECTION_NAME not found: " + name)
        else:
            click.echo("Found COLLECTION_NAME: " + name)
    return picked_object


def print_info(name):
    wrapper = lookup_collection(name)
    c = json_helper.load_and_validate(COLLECTION_FILENAME, _dir=wrapper.get('location'))
    print_helper.print_json(c)


def lookup_collection(name):
    _list = json_helper.read_collection_list()

    for c in _list:
        if name is None and c.get('_current', False):
            return c
        if name is not None and name == c.get('name', None):
            return c
        if name is not None and name == str(c.get('number', 0)):
            return c
    else:
        return None
