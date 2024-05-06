import click

from rc3.common import json_helper, print_helper


@click.command("settings", short_help="Prints RC/settings.json.")
def cli():
    """\b
    Will print the current global settings.json to STDOUT.

    \b
    I recommend editing settings & global env json in VSCode.
    You should be able to launch VSCode @ RC_HOME root with:
    code $(rc home)
    """

    settings = json_helper.read_settings()
    print_helper.print_json(settings)
