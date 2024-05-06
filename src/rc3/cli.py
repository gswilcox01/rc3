import os
import click

from rc3.common import json_helper, config_helper, rc_globals

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
        # See more options like unique prefix matching here:
        # https://click.palletsprojects.com/en/8.1.x/advanced/#command-aliases
        aliases = {
            'r': 'request',
            'c': 'collection',
            'e': 'environment'
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
    json_helper.validate_schemas()

    # Note: this next cmd will always create RC_HOME / ~/.rc if it doesn't exist
    home = config_helper.get_config_folder()
    dest = os.path.join(home, 'settings.json')
    if os.path.exists(dest):
        # validate the RC/settings.json file (& sys.exit() if invalid)
        json_helper.load_and_validate('settings.json')


