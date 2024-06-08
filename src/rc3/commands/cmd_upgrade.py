import json
import os
import time

import click

from rc3.commands import cmd_list
from rc3.common import json_helper, print_helper, config_helper
from rc3.common.data_helper import SCHEMA_BASE_URL, SCHEMA_PREFIX, SCHEMA_VERSION


@click.command("upgrade", short_help="Attempt to upgrade the current COLLECTION.")
def cli():
    """\b
    Upgrade the current collection where possible to your current version of the rc CLI.

    """
    show_fake_progress()


def show_fake_progress():
    print("Checking for possible upgrades...")
    with click.progressbar(range(16)) as bar:
        for x in bar:
            time.sleep(.25)
    click.confirm("Would you like to upgrade the EXAMPLE REQUESTS in this collection", default=True)
    print("Done.")
    click.confirm("Would you like to upgrade REQUEST SCHEMA references to the latest 0.0.9 in this collection", default=True)
    print("Done.")
    click.confirm("Would you like to upgrade REQUEST extract[*] format in this collection", default=True)
    print("Done.")
