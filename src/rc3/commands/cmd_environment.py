import json
import os
import click

from rc3.commands import cmd_list
from rc3.common import json_helper, print_helper, config_helper
from rc3.common.data_helper import SCHEMA_BASE_URL, SCHEMA_PREFIX, SCHEMA_VERSION


@click.command("collection", short_help="Manage ENVIRONMENTS defined in a collection.")
@click.option('-l', '--list', '_list', is_flag=True, default=False, help="List ENVIRONMENTS in a collection.")
@click.option('-i', '--info', is_flag=True, default=False, help="Display json of current ENVIRONMENT.")
@click.option('-n', '--new', is_flag=True, default=False, help="Create a new ENVIRONMENT in a collection.")
@click.option('-p', '--pick', is_flag=True, default=False, help="Pick an item as current ENVIRONMENT.")
@click.option('-e', '--edit', is_flag=True, default=False, help="Edit an ENVIRONMENT with system editor.")
@click.argument('environment_name', type=str, required=False)
def cli(_list, info, new, pick, edit, environment_name):
    """\b
    Manages ENVIRONMENTS in the current_collection.

    \b
    ENVIRONMENT_NAME is optional.
    ENVIRONMENT_NAME will default to the current_environment, or prompt you to pick.
    ENVIRONMENT_NAME if used should be one of:
    1. The NUM column from 'rc environment --list' output
    2. THe NAME column from 'rc environment --list' output
    """
    if _list:
        cmd_list.list_environments()
    elif new:
        create_environment(environment_name)
    elif edit:
        edit_environment(environment_name)
    elif info:
        print_info(environment_name)
    elif pick:
        pick_environment(environment_name)
    elif environment_name is None:
        # DEFAULT to list() if no ENVIRONMENT_NAME
        cmd_list.list_environments()
    else:
        # DEFAULT to pick() if ENVIRONMENT_NAME
        pick_environment(environment_name)


def pick_environment(name=None):
    e = lookup_or_prompt(name)
    if e is None:
        return None

    c, c_wrapper = json_helper.read_current_collection()
    c['current_environment'] = e['name']
    json_helper.write_collection(c_wrapper)

    click.echo("ENVIRONMENT has been picked: " + e['name'])
    return e


def edit_environment(name, e=None):
    if e is None:
        e = lookup_environment(name)
    if e is None:
        raise click.ClickException("ENVIRONMENT '{}' not found. See 'rc environment --list'".format(name))
    new = internal_edit(e)
    if new is not None:
        e['_original'] = new
        save_environment(e, new)
    return e


def internal_edit(r):
    json_string = print_helper.get_json_string(r.get('_original'))
    new_string = click.edit(json_string)
    if new_string is not None:
        new_e = json_helper.parse_json(new_string)
        if new_e is None:
            raise click.ClickException("new ENVIRONMENT must be valid JSON.")
        if json_helper.validate(new_e, 'environment'):
            return new_e
    else:
        return None


def lookup_or_prompt(name, prompt="Which ENVIRONMENT do you want to pick?"):
    _list = json_helper.read_environment_list()
    if len(_list) == 0:
        raise click.ClickException("Invalid option.  There are no ENVIRONMENTS defined.")

    picked_object = None
    if name is None:
        cmd_list.list_environments()
        e = lookup_environment(None)
        default_choice = 0 if e is None else e.get('number', 0)
        number = click.prompt(prompt, default=default_choice)
        picked_object = lookup_environment(str(number))
        if picked_object is None:
            raise click.ClickException("Invalid selection")
    else:
        picked_object = lookup_environment(name)
        if picked_object is None:
            raise click.ClickException("ENVIRONMENT_NAME not found: " + name)
        else:
            click.echo("Found ENVIRONMENT_NAME: " + name)
    return picked_object


def print_info(name):
    e = lookup_environment(name)
    print_helper.print_json(e['_original'])


def lookup_environment(name):
    _list = json_helper.read_environment_list()

    for e in _list:
        if name is None and e.get('_current', False):
            return e
        if name is not None and name == e.get('name', None):
            return e
        if name is not None and name == str(e.get('number', 0)):
            return e
    else:
        return None


def save_environment(e, new):
    json_helper.write_environment(e['_filename'], new)
    print("ENVIRONMENT saved: " + e['name'])


def create_environment(name):
    name = config_helper.clean_filename(name)
    display_name = '' if name is None else name
    click.echo(f'Creating new ENVIRONMENT {display_name}')

    schema = json_helper.read_schema('environment')
    env = {
        "$schema": schema['$id'],
        "baseUrl": "http://localhost:8080",
        "property1": "value1"
    }

    if name is None:
        name = click.prompt("Enter a short NAME for this ENVIRONMENT", default=display_name)
        name = config_helper.clean_filename(name)

    # Check if existing ENV, and confirm overwrite
    _list = json_helper.read_environment_list()
    for e in _list:
        if name == e['name']:
            if not click.confirm("An ENVIRONMENT named '{}' already exists, do you want to overwrite it?".format(name)):
                raise click.Abort()

    env['baseUrl'] = click.prompt("Enter the BASE URL for this ENVIRONMENT", default=env['baseUrl'])
    json_helper.write_environment(name+".json", env)
    print("ENVIRONMENT created: " + name)

