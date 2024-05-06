import os
import click
from rc3.common import config_helper, json_helper, data_helper
from rc3.common.data_helper import SETTINGS_FILENAME, COLLECTION_FILENAME, GLOBAL_ENV_FILENAME


@click.command("init", short_help="Init RC settings, and Collection files.")
def cli():
    """\b
    Will do 0-4 of the following:
    1. Will create the RC_HOME directory if it doesn't exist.
    2. Will create RC_HOME/settings, global env, and schemas dir if they don't exist.
    3. Will initialize a new example Collection if ran from an empty directory.
    4. Will import the current directory if it contains a valid rc-collection.json file.
    """

    # do the 0-4 things
    init_rc_home()
    init_cwd_as_collection()
    import_collection()


def init_cwd_as_collection():
    cwd = os.getcwd()
    if not os.listdir(cwd):
        print("CWD is empty, creating sample Collection here: " + cwd)
        data_helper.copy_tree('collection', cwd)
    else:
        print("CWD is not empty, skipping collection creation...")


def import_collection():
    cwd = os.getcwd()
    print("Importing collection from: " + cwd)
    collection_dict = json_helper.load_and_validate(COLLECTION_FILENAME, _dir=cwd)
    if collection_dict is None:
        return

    # get "name" from json, or use cwd directory name
    parts = os.path.split(cwd)
    name = collection_dict.get("name", parts[-1])

    settings = json_helper.read_settings()
    settings["current_collection"] = name
    # ONLY add to the collections list if name is NOT already there!
    if any(filter(lambda c: c['name'] == name, settings['collections'])):
        print("Name already exists in global settings: " + name)
    else:
        print("Adding collection to global settings: " + name)
        settings["collections"].append({
            "name": name,
            "location": cwd
        })
    json_helper.write_settings(settings)


def init_rc_home():
    # Note: this next cmd will always create RC_HOME / ~/.rc if it doesn't exist
    home = config_helper.get_config_folder()

    dest = os.path.join(home, SETTINGS_FILENAME)
    if not os.path.exists(dest):
        print("Creating " + dest)
        data_helper.copy('home/' + SETTINGS_FILENAME, dest)

    dest = os.path.join(home, GLOBAL_ENV_FILENAME)
    if not os.path.exists(dest):
        print("Creating " + dest)
        data_helper.copy('home/' + GLOBAL_ENV_FILENAME, dest)

    dest = os.path.join(home, 'schemas')
    if not os.path.exists(dest):
        print("Creating " + dest)
        data_helper.copy_tree('home/schemas', dest)
