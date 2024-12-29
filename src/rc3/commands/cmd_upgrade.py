import hashlib
import json
import os
import re
import time
from importlib import resources

import click

from rc3.commands import cmd_list
from rc3.common import json_helper, print_helper, config_helper, data_helper
from rc3.common.data_helper import SCHEMA_BASE_URL, SCHEMA_PREFIX, SCHEMA_VERSION, SETTINGS_FILENAME, \
    GLOBAL_ENV_FILENAME, KEYRING_FILENAME


@click.command("upgrade", short_help="Upgrade schemas & files in current COLLECTION & RC_HOME.")
def cli():
    """\b
    Upgrade the current collection where possible to your current version of the rc CLI.

    """
    print("Checking for possible upgrades...")
    check_home_schemas()
    check_collection_examples()
    check_collection_schemas()
    check_collection_extract()
    check_collection_json()


def check_home_schemas():
    click.echo("Checking RC_HOME schemas...", nl=False)
    buffer = []
    home = config_helper.get_config_folder()

    # check settings
    settings_dest = os.path.join(home, SETTINGS_FILENAME)
    settings = json_helper.read_json(settings_dest)
    settings_schema = json_helper.read_schema('settings')
    if settings['$schema'] != settings_schema['$id']:
        if len(buffer) == 0:
            click.echo(click.style(f' UPGRADES NEEDED', fg='red'))
        buffer.append(f'settings schema is({settings['$schema']}) but should be({settings_schema['$id']})')

    # check global
    global_dest = os.path.join(home, GLOBAL_ENV_FILENAME)
    global_env = json_helper.read_json(global_dest)
    env_schema = json_helper.read_schema('environment')
    if global_env['$schema'] != env_schema['$id']:
        if len(buffer) == 0:
            click.echo(click.style(f' UPGRADES NEEDED', fg='red'))
        buffer.append(f'global_env schema is({global_env['$schema']}) but should be({env_schema['$id']})')

    # check keyring
    keyring_fn = os.path.join(home, KEYRING_FILENAME)
    keyring_history = json_helper.read_json(keyring_fn)
    keyring_schema = json_helper.read_schema('keyring')
    if keyring_history['$schema'] != keyring_schema['$id']:
        if len(buffer) == 0:
            click.echo(click.style(f' UPGRADES NEEDED', fg='red'))
        buffer.append(f'keyring_history schema is({keyring_history['$schema']}) but should be({keyring_schema['$id']})')

    if len(buffer) == 0:
        click.echo(click.style(f' OK', fg='green'))
        return

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
    if keyring_history['$schema'] != keyring_schema['$id']:
        keyring_history['$schema'] = keyring_schema['$id']
        json_helper.write_environment(KEYRING_FILENAME, keyring_history)
    click.echo(click.style(f' SUCCESS', fg='green'))


def check_collection_schemas():
    click.echo("Checking current COLLECTION schemas...", nl=False)

    # check for current collection
    c, wrapper = json_helper.read_current_collection()
    if c is None:
        click.echo(click.style(f' No current COLLECTION exists', fg='red'))
        return
    c_folder = wrapper['_dir']
    update_files = {}

    # RE out the partial name "request" from the following string
    # rc3-request-0.0.3.json
    exclude = {'.git'}
    schema_re = re.compile(r'rc3-([a-z]*)-\d.\d.\d.json')
    for root, dirs, files in os.walk(c_folder):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file in files:
            full_file = os.path.join(root, file)
            # print(full_file)
            full_json = json_helper.read_json_or_none(full_file)
            actual_schema = None if full_json is None else full_json.get('$schema', None)
            if actual_schema is not None:
                match = schema_re.search(actual_schema)
                if match is not None:
                    partial = match.group(1)
                    schema = json_helper.read_schema(partial)
                    expected_schema = schema['$id']
                    if expected_schema != actual_schema:
                        if len(update_files) == 0:
                            click.echo(click.style(f' UPGRADES NEEDED', fg='red'))
                        click.echo(f'{file}')
                        click.echo(f'      schema is: {actual_schema}')
                        click.echo(f'  but should be: {expected_schema}')
                        update_files[full_file] = expected_schema

    if len(update_files) == 0:
        click.echo(click.style(f' OK', fg='green'))
        return

    if not click.confirm("Would you like to upgrade current COLLECTION schemas", default=True):
        return

    click.echo("Upgrading current COLLECTION schemas...", nl=False)
    for full_file, expected_schema in update_files.items():
        full_json = json_helper.read_json_or_none(full_file)
        full_json['$schema'] = expected_schema
        json_helper.write_json(full_file, full_json)
    click.echo(click.style(f' SUCCESS', fg='green'))


def check_collection_examples():
    click.echo("Checking current COLLECTION examples...", nl=False)

    # determine current collection examples folder
    c, wrapper = json_helper.read_current_collection()
    if c is None:
        click.echo(click.style(f' No current COLLECTION exists', fg='red'))
        return
    c_folder = wrapper['_dir']
    examples_folder = os.path.join(c_folder, 'examples')

    # data_helper.walk_tree('collection/examples')
    missing_count = 0
    changed_count = 0
    reference_examples_folder = data_helper.get_file('collection/examples')
    with resources.as_file(reference_examples_folder) as path:
        for dirpath, dirnames, files in os.walk(path):
            for file in files:
                ref_file = os.path.join(dirpath, file)
                ref_hash = sha256(ref_file)
                col_file = os.path.join(examples_folder, file)
                if os.path.exists(col_file):
                    col_hash = sha256(col_file)
                    if ref_hash != col_hash:
                        changed_count += 1
                else:
                    missing_count += 1

    if missing_count + changed_count == 0:
        click.echo(click.style(f' OK', fg='green'))
        return
    click.echo(click.style(f' UPGRADES NEEDED', fg='red'))

    click.echo(f'Example folder has {changed_count} out-of-date examples, {missing_count} missing examples...')
    if not click.confirm("Would you like to create/update current COLLECTION examples", default=True):
        return
    click.echo("Updating current COLLECTION examples...", nl=False)
    data_helper.copy_tree('collection/examples', examples_folder)
    click.echo(click.style(f' SUCCESS', fg='green'))


def sha256(filename):
    with open(filename, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def check_collection_extract():
    click.echo("Checking current COLLECTION REQUEST extract JSON...", nl=False)
    click.echo(click.style(f' NOT IMPLEMENTED YET', fg='yellow'))


def check_collection_json():
    click.echo("Checking current COLLECTION validating JSON against current schemas...", nl=False)
    click.echo(click.style(f' NOT IMPLEMENTED YET', fg='yellow'))

