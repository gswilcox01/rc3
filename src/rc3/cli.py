import os
import re

import click

from rc3.common import json_helper, config_helper, rc_globals
from rc3.common.data_helper import SETTINGS_FILENAME

cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "commands"))


# based on: https://github.com/pallets/click/blob/main/examples/complex/complex/cli.py
class ComplexCLI(click.Group):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and filename.startswith("cmd_"):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        # See other options like unique prefix matching here:
        # https://click.palletsprojects.com/en/8.1.x/advanced/#command-aliases

        # try to ignore typos
        if re.match('^co', name, re.I):
            name = 'collection'
        elif re.match('^env', name, re.I):
            name = 'environment'
        elif re.match('^glo', name, re.I):
            name = 'global'
        elif re.match('^hel', name, re.I):
            name = 'hello'
        elif re.match('^imp', name, re.I):
            name = 'import'
        elif re.match('^li', name, re.I):
            name = 'list'
        elif re.match('^req', name, re.I):
            name = 'request'
        elif re.match('^sen', name, re.I):
            name = 'send'
        elif re.match('^set', name, re.I):
            name = 'settings'

        # shortcuts/aliases
        aliases = {
            's': 'send',
            'r': 'request',
            'c': 'collection',
            'e': 'environment',
            'g': 'global'
        }
        name = aliases.get(name, name)
        try:
            mod = __import__(f"rc3.commands.cmd_{name}", None, None, ["cli"])
        except ImportError:
            return
        return mod.cli


@click.command(cls=ComplexCLI)
@click.pass_context
@click.option('-v', '--verbose', is_flag=True, default=False, help="Verbose output.")
def cli(ctx, verbose):
    """A REST CLI for configuring & executing COLLECTIONS of REQUESTS
    """

    # add to global cli_options
    cli_options = rc_globals.get_cli_options()
    cli_options['verbose'] = verbose

    # validate all the schemas in the project
    # json_helper.validate_schemas()

    # create RC_HOME, settings, global.env, /schema dir (if missing/needed)
    config_helper.init_rc_home()

    # FAILFAST if bad RC_HOME/settings.json
    home = config_helper.get_config_folder()
    dest = os.path.join(home, SETTINGS_FILENAME)
    if os.path.exists(dest):
        # validate the RC/settings.json file (& sys.exit() if invalid)
        json_helper.load_and_validate(SETTINGS_FILENAME)


