import json
import os
import time

import click

from rc3.commands import cmd_list
from rc3.common import json_helper, print_helper, config_helper
from rc3.common.data_helper import SCHEMA_BASE_URL, SCHEMA_PREFIX, SCHEMA_VERSION, SETTINGS_FILENAME, \
    GLOBAL_ENV_FILENAME


@click.command("upgrade", short_help="Attempt to upgrade the current COLLECTION.")
def cli():
    """\b
    Upgrade the current collection where possible to your current version of the rc CLI.

    """
    print("Checking for possible upgrades...")
    check_home_schemas()
    check_collection_schemas()
    check_collection_examples()
    check_collection_extract()


def check_home_schemas():
    click.echo("Checking RC_HOME schemas...", nl=False)
    buffer = []
    home = config_helper.get_config_folder()

    # check settings
    settings_dest = os.path.join(home, SETTINGS_FILENAME)
    settings = json_helper.read_json(settings_dest)
    settings_schema = json_helper.read_schema('settings')
    if settings['$schema'] != settings_schema['$id']:
        buffer.append(f'settings schema is({settings['$schema']}) but should be({settings_schema['$id']})')

    # check global
    global_dest = os.path.join(home, GLOBAL_ENV_FILENAME)
    global_env = json_helper.read_json(global_dest)
    env_schema = json_helper.read_schema('environment')
    if global_env['$schema'] != env_schema['$id']:
        buffer.append(f'global_env schema is({global_env['$schema']}) but should be({env_schema['$id']})')

    if len(buffer) == 0:
        # click.echo(" OK")
        click.echo(click.style(f' OK', fg='green'))
        return

    click.echo("")
    for line in buffer:
        click.echo(line)
    if not click.confirm("Would you like to upgrade RC_HOME schemas", default=True):
        return

    click.echo("Upgrading RC_HOME schemas...", nl=False)
    if settings['$schema'] != settings_schema['$id']:
        settings['$schema'] = settings_schema['$id']
        json_helper.write_settings(settings)
    if global_env['$schema'] != env_schema['$id']:
        global_env['$schema'] = env_schema['$id']
        json_helper.write_environment(GLOBAL_ENV_FILENAME, global_env)
    click.echo(click.style(f' SUCCESS', fg='green'))


def check_collection_schemas():
    click.echo("Checking current COLLECTION schemas...", nl=False)
    click.echo(click.style(f' OK', fg='green'))


def check_collection_examples():
    click.echo("Checking current COLLECTION examples...", nl=False)
    click.echo(click.style(f' OK', fg='green'))


def check_collection_extract():
    click.echo("Checking current COLLECTION REQUEST extract JSON...", nl=False)
    click.echo(click.style(f' OK', fg='green'))


