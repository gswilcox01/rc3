import click

from rc3.common import json_helper, print_helper

@click.command("settings", short_help="Manage the GLOBAL RC SETTINGS stored at RC_HOME.")
@click.option('-i', '--info', is_flag=True, default=False, help="Display json of RC-SETTINGS.")
@click.option('-e', '--edit', is_flag=True, default=False, help="Edit the RC-SETTINGS file with system editor.")
def cli(info, edit):
    """\b
    Manage the GLOBAL RC-SETTINGS stored at RC_HOME.

    Alternatively, I recommend editing rc-settings & rc-global env in VSCode,
    where schema hints & validations will be shown.

    """

    if edit:
        edit_settings()
    elif info:
        print_info()
    else:
        print_info()


def edit_settings():
    settings = json_helper.read_settings()
    new = internal_edit(settings)
    if new is not None:
        json_helper.write_settings(new)


def internal_edit(settings):
    json_string = print_helper.get_json_string(settings)
    new_string = click.edit(json_string)
    if new_string is not None:
        new = json_helper.parse_json(new_string)
        if new is None:
            raise click.ClickException("new SETTINGS must be valid JSON.")
        if json_helper.validate(new, 'settings'):
            return new
    else:
        return None


def print_info():
    settings = json_helper.read_settings()
    print_helper.print_json(settings)
