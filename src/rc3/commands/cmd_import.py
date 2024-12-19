import os
import shutil

import click

from rc3.commands import cmd_new
from rc3.common import config_helper, json_helper, data_helper
from rc3.common.data_helper import SETTINGS_FILENAME, COLLECTION_FILENAME, GLOBAL_ENV_FILENAME


@click.command("import", short_help="Import an existing Collection from CWD")
def cli():
    """\b
    Must be run from a directory with a valid rc-collection.json.
    Will:
    1. Import the collection into RC_HOME/rc-settings.json
    """

    valid_collection_check()
    cmd_new.import_collection()


def valid_collection_check():
    cwd = os.getcwd()
    dest = os.path.join(cwd, COLLECTION_FILENAME)
    if not os.path.exists(dest):
        raise click.ClickException("CWD must contain a valid rc-collection.json file")
