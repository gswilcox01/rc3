from datetime import datetime

import keyring
from keyring.errors import PasswordDeleteError

from rc3.common import json_helper


def create_date_string():
    now = datetime.now()
    return now.isoformat()


def find_in_history(name):
    keyring_history = json_helper.read_keyring()
    for e in keyring_history['entries']:
        if e.get("name") == name:
            return e
    return {
        "name": name
    }


def save_to_history(entry):
    keyring_history = json_helper.read_keyring()

    # find existing entry
    existing = None
    for e in keyring_history['entries']:
        if e.get("name") == entry.get("name"):
            existing = e

    # append, or update existing entry
    if existing is None:
        keyring_history['entries'].append(entry)
    else:
        for key in entry:
            existing[key] = entry[key]

    # save it
    json_helper.write_keyring(keyring_history)


def delete_from_history(name):
    keyring_history = json_helper.read_keyring()
    new_entries = [entry for entry in keyring_history['entries'] if entry.get("name") != name]
    keyring_history['entries'] = new_entries

    # save it
    json_helper.write_keyring(keyring_history)


def get_value(name):
    entry = find_in_history(name)
    value = keyring.get_password("rc3", name)

    if value is not None and len(value) > 0:
        entry["accessed"] = create_date_string()
        save_to_history(entry)

    return value


def delete_value(name):
    try:
        keyring.delete_password("rc3", name)
    except PasswordDeleteError as e:
        pass

    delete_from_history(name)


def set_value(name, password):
    entry = find_in_history(name)
    keyring.set_password("rc3", name, password)

    if "created" not in entry:
        entry['created'] = create_date_string()
    entry['modified'] = create_date_string()
    save_to_history(entry)
