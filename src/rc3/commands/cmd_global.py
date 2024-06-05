import json
import os
import click

from rc3.commands import cmd_list
from rc3.common import json_helper, print_helper, config_helper
from rc3.common.data_helper import SCHEMA_BASE_URL, SCHEMA_PREFIX, SCHEMA_VERSION


@click.command("global", short_help="Manage the GLOBAL ENVIRONMENT stored at RC_HOME.")
@click.option('-i', '--info', is_flag=True, default=False, help="Display json of GLOBAL ENVIRONMENT.")
@click.option('-e', '--edit', is_flag=True, default=False, help="Edit the GLOBAL ENVIRONMENT with system editor.")
def cli(info, edit):
    """\b
    Manage the GLOBAL ENVIRONMENT stored at RC_HOME.

    """
    if edit:
        edit_environment()
    elif info:
        print_info()
    else:
        print_info()


def edit_environment():
    env_filename, env = json_helper.read_environment('global')
    new = internal_edit(env)
    if new is not None:
        json_helper.write_environment(env_filename, new)


def internal_edit(env):
    json_string = print_helper.get_json_string(env)
    new_string = click.edit(json_string)
    if new_string is not None:
        new_e = json_helper.parse_json(new_string)
        if new_e is None:
            raise click.ClickException("new ENVIRONMENT must be valid JSON.")
        if json_helper.validate(new_e, 'environment'):
            return new_e
    else:
        return None


def print_info():
    env_filename, env = json_helper.read_environment('global')
    print_helper.print_json(env)
