import keyring


def get_value(name):
    return keyring.get_password("rc3", name)


def delete_value(name):
    keyring.delete_password("rc3", name)


def set_value(name, password):
    keyring.set_password("rc3", name, password)


