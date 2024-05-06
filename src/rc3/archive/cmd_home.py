import click

from rc3.common import config_helper


@click.command("home", short_help="Prints RC_HOME directory.")
def cli():
    """\b
    Will print the RC_HOME directory to STDOUT.

    \b
    I recommend editing settings & global env json in VSCode.
    You should be able to launch VSCode @ RC_HOME root with:
    code $(rc home)
    """

    home = config_helper.get_config_folder()
    print(home)
