import os
import shutil

import click
from rc3.common import config_helper, json_helper, data_helper
from rc3.common.data_helper import SETTINGS_FILENAME, COLLECTION_FILENAME, GLOBAL_ENV_FILENAME


@click.command("new", short_help="Create a new Collection in CWD")
def cli():
    """\b
    Must be run from an empty directory.
    Will:
    1. Create a new rc-collection.json
    2. Optionally create example Requests
    3. Import your new collection into RC_HOME/rc-settings.json
    """

    empty_cwd_check()
    init_cwd_as_collection()
    import_collection()


def empty_cwd_check():
    cwd = os.getcwd()
    if os.listdir(cwd):
        print("CWD must be empty to create a new collection.")
        dest = os.path.join(cwd, COLLECTION_FILENAME)
        if os.path.exists(dest):
            print("Try 'rc import' to import an existing collection...")
        raise click.Abort()


def init_cwd_as_collection():
    cwd = os.getcwd()
    dir_name = os.path.basename(cwd)
    name = click.prompt("Enter a NAME for this COLLECTION", default=dir_name)
    include_examples = click.confirm("Include example Requests in your new collection?", default=True, show_default=True)
    if include_examples:
        # copy the entire example collection
        data_helper.copy_tree('collection', cwd)
    else:
        # copy JUST environments and the rc-collection file
        env_dir = os.path.join(cwd, 'environments')
        data_helper.copy_tree('collection/environments', env_dir)
        data_helper.copy('collection/rc-collection.json', cwd)

    c, wrapper = json_helper.read_collection(_dir=cwd)
    c['name'] = name
    if not include_examples:
        c['current_request'] = ""
    json_helper.write_collection(wrapper)


def import_collection():
    cwd = os.getcwd()
    print("Importing collection into RC_HOME/rc-settings.json")
    collection_dict = json_helper.load_and_validate(COLLECTION_FILENAME, _dir=cwd)
    if collection_dict is None:
        return

    # get "name" from json, or abort
    name = collection_dict.get("name", None)
    if name is None:
        raise click.ClickException("Error: rc-collection.json doesn't have a valid name attribute")

    # for any .defaults environments in the collection, copy them to .json (i.e. make a real environment)
    # note: there should also be a .gitignore in the env folder, so .json doesn't get committed
    env_folder = os.path.join(cwd, 'environments')
    defaults_counter = 0
    for dirpath, dirnames, files in os.walk(env_folder):
        for file in files:
            if file.endswith('.defaults'):
                env_name = file.split('.')[-2]
                default_file = os.path.join(dirpath, file)
                new_file = os.path.join(dirpath, env_name + ".json")
                if not os.path.exists(new_file):
                    defaults_counter += 1
                    shutil.copy(default_file, new_file)
    # if defaults_counter > 0:
    #     print(f"{defaults_counter} default environment(s) initialized in your collection")

    settings = json_helper.read_settings()
    settings["current_collection"] = name

    # if collection name already exists, just update the location pointer
    # NOTE: the old collection location will disappear from settings...
    found = False
    for cp in settings['collections']:
        if cp['name'] == name:
            cp['location'] = cwd
            found = True
            break
    if not found:
        settings["collections"].append({
            "name": name,
            "location": cwd
        })
    json_helper.write_settings(settings)
    # print(f"Collection '{name}' has been imported successfully, try 'rc list' to see available Requests.")
    print(f"Collection '{name}' has been successfully imported, try 'rc list' next...")
