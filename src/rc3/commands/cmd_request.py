import json
import os
import click

from rc3.commands import cmd_list
from rc3.common import json_helper, print_helper


@click.command("request", short_help="Manage REQUESTS in current_collection.")
@click.option('-l', '--list', '_list', is_flag=True, default=False, help="List REQUESTS in collection.")
@click.option('-n', '--new', is_flag=True, default=False, help="Create a new REQUEST.")
@click.option('-i', '--info', is_flag=True, default=False, help="Display json of current REQUEST.")
@click.option('-p', '--pick', is_flag=True, default=False, help="Pick an item as current REQUEST.")
@click.option('-e', '--edit', is_flag=True, default=False, help="Edit a REQUEST with system editor.")
@click.argument('request_name', type=str, required=False)
def cli(_list, new, info, pick, edit, request_name):
    """\b
    Manages REQUEST objects/files in the current collection.

    \b
    REQUEST_NAME is optional.
    REQUEST_NAME will default to the current_request, or prompt you to pick.
    REQUEST_NAME if used should be one of:
    1. The NUM column from 'rc request --list' output
    2. THe NAME column from 'rc request --list' output

    """
    if _list:
        cmd_list.list_requests()
    elif new:
        click.echo("NOT IMPLEMENTED! Please use VSCode to edit your collection.")
    elif edit:
        edit_request(request_name)
    elif info:
        print_info(request_name)
    elif pick:
        pick_request(request_name)
    elif request_name is None:
        # DEFAULT to list() if no REQUEST_NAME
        cmd_list.list_requests()
    else:
        # DEFAULT to pick() if REQUEST_NAME
        pick_request(request_name)


def pick_request(name=None):
    r = lookup_or_prompt(name)
    if r is None:
        return None

    c, c_wrapper = json_helper.read_current_collection()
    c['current_request'] = r.get('_short_request', '')

    json_helper.write_collection(c_wrapper)
    click.echo("REQUEST has been picked: " + r.get('_display_ref'))
    return r


def edit_request(name, wrapper=None):
    if wrapper is None:
        wrapper = lookup_request(name)
    if wrapper is None:
        raise click.ClickException("REQUEST '{}' not found. See 'rc request --list'".format(name))
    r = internal_edit(wrapper)
    if r is not None:
        save_request(r, wrapper)
        wrapper['_original'] = r
    return wrapper


def internal_edit(wrapper):
    json_string = print_helper.get_json_string(wrapper.get('_original'))
    new_string = click.edit(json_string)
    if new_string is not None:
        r = json_helper.parse_json(new_string)
        if r is None:
            raise click.ClickException("new REQUEST must be valid JSON.")
        if json_helper.validate(r, 'request'):
            return r
    else:
        return None


def lookup_or_prompt(name, prompt="Which REQUEST do you want to pick?"):
    _list = json_helper.read_request_list()
    if len(_list) == 0:
        raise click.ClickException("Invalid option.  There are no REQUESTS defined.")

    picked_object = None
    if name is None:
        cmd_list.list_requests()
        current_r = lookup_request(None)
        default_choice = 0 if current_r is None else current_r.get('number', 0)
        number = click.prompt(prompt, default=default_choice)
        picked_object = lookup_request(str(number))
        if picked_object is None:
            raise click.ClickException("Invalid selection")
    else:
        picked_object = lookup_request(name)
        if picked_object is None:
            raise click.ClickException("REQUEST_NAME not found: " + name)
        else:
            click.echo("Found REQUEST_NAME: " + name)
    return picked_object


def print_info(request_name):
    r = lookup_request(request_name)
    print(r.get('_display_ref'))
    print_helper.print_json(r.get('_original', None))


def lookup_request(name):
    _list = json_helper.read_request_list()

    for r in _list:
        if name is None and r.get('_current', False):
            return r
        if name is not None and name == r.get('name', None):
            return r
        if name is not None and name == str(r.get('number', 0)):
            return r
    else:
        return None


def save_request(r, wrapper):
    json_helper.write_request(r, wrapper)
    print("REQUEST saved: ")
    print(wrapper.get('_display_ref'))

