import click

from rc3.common import json_helper


@click.command("root", short_help="Prints CURRENT_COLLECTION directory.")
def cli():
    """\b
    Will print the current collection directory (from settings.json) to STDOUT.

    \b
    I recommend editing collection & request json in VSCode.
    You should be able to launch VSCode @ collection root with:
    code $(rc root)
    """

    current_collection = json_helper.find_current_collection()
    if current_collection is None:
        print("No current_collection selected!")
    else:
        print(current_collection.get('location', "No location set in current_collection!"))
