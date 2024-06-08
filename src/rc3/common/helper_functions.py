import json
import os
import re
import uuid

import click
import pkce
from click import prompt

from rc3.common import json_helper, print_helper, decorators, file_helper


def lookup_helper_value(var):
    # simple hard-coding for now
    # in the future maybe dynamically use any function in this file, or even add user-defined helper functions
    if var.startswith("#pkce_cvcc"):
        return pkce_cvcc(var)
    if var.startswith("#uuid"):
        return uuid_helper(var)
    if var.startswith("#prompt"):
        return prompt_helper(var)
    if var.startswith("#file"):
        return file_helper_function(var)
    raise click.ClickException(
        f'handlebar helper_function [{var}] is invalid!')


def parse_env_var(var):
    parts = var.split()
    helper_name = parts[0]
    var_name = None
    env_name = "global"
    if len(parts) > 1:
        var_name = parts[1]
        var_parts = var_name.split('.')
        if len(var_parts) > 1:
            env_name = var_parts[0]
            var_name = var_parts[1]
            if env_name not in ['global', 'current']:
                raise click.ClickException(
                    f'Env name in {helper_name} helper function must be global or current. [{env_name}] is invalid!')
    return env_name, var_name


def pkce_cvcc(var):
    # initial impl, uses default/mostly fixed values of
    # length = 128
    # global var to store = code_verifier
    # challenge transformation = S256
    parts = var.split()
    env_name, var_name = parse_env_var(var)
    if var_name is None:
        var_name = 'code_verifier'
    if len(parts) > 2:
        raise click.ClickException(
            f'Invalid # of parameters to {parts[0]} helper function.  Expected 0 or 1, but got {len(parts)}!')

    # generate cv and cc
    cv, cc = pkce.generate_pkce_pair()

    # store cv into global env
    env_filename, env = json_helper.read_environment(env_name)
    env[var_name] = cv
    json_helper.write_environment(env_filename, env)

    # bust the cache, so future reads in same process see the change
    decorators.rc_clear_cache('read_environment')

    # return cc, to be populated in template
    return cc


def uuid_helper(var):
    # initial impl
    # type = uuid4
    # no parameter = NO var
    # parameter with no . = stored in global
    # parameter with . = LEFT side must be global|current RIGHT side is var name
    parts = var.split()
    env_name, var_name = parse_env_var(var)
    if len(parts) > 2:
        raise click.ClickException(
            f'Invalid # of parameters to #uuid helper function.  Expected 0 or 1, but got {len(parts)}!')

    # generate
    value = str(uuid.uuid4())

    # store in env
    if var_name is not None:
        env_filename, env = json_helper.read_environment(env_name)
        env[var_name] = value
        json_helper.write_environment(env_filename, env)

    # bust the cache, so future reads in same process see the change
    decorators.rc_clear_cache('read_environment')

    # return the uuid
    return value


def prompt_helper(var):
    parts = var.split()
    if len(parts) < 2:
        raise click.ClickException('A prompt is required when using the #prompt helper function!')

    # look for a prompt + default
    p = var[8:]
    parts = p.split(":")
    default = ""
    if len(parts) > 1:
        p = parts[0]
        default = parts[1]

    # prompt for value, and return
    return click.prompt(p, default=default)


def file_helper_function(var):
    # IMPORTANT! preprocess_file_option() MUST have been called back in cmd_send BEFORE env subs/helpers are called!
    parts = var.split()
    if len(parts) > 1:
        raise click.ClickException('The #file helper function doesn\'t support any parameters!')
    if not file_helper.state['has_file']:
        raise click.ClickException('The --file option must be used since this request has a #file helper function!')

    # ALWAYS return as a string
    # if subbing into the JSON body, the string will get converted back to JSON/dict after subs
    return file_helper.consume_as_string()



