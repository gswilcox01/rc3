import json
import os
import re
import click
import pkce

from rc3.common import json_helper, print_helper, decorators


def lookup_helper_value(var):
    # simple hard-coding for now
    # in the future maybe dynamically use any function in this file, or even add user-defined helper functions
    if var.startswith("#pkce_vc"):
        return pkce_vc(var)
    raise click.ClickException(
        f'handlebar helper_function [{var}] is invalid!')


def pkce_vc(var):
    # initial impl, uses default/mostly fixed values of
    # length = 128
    # global var to store = code_verifier
    # challenge transformation = S256
    parts = var.split()
    cv_var = 'code_verifier'
    if len(parts) > 1:
        cv_var = parts[1]
    if len(parts) > 2:
        raise click.ClickException(
            f'Invalid # of parameters to #pkce_vc helper function.  Expected 0 or 1, but got {len(parts)}!')

    # generate cv and cc
    cv, cc = pkce.generate_pkce_pair()

    # store cv into global env
    env_filename, env = json_helper.read_environment('global')
    env[cv_var] = cv
    json_helper.write_environment(env_filename, env)

    # bust the cache, so future reads in same process see the change
    decorators.rc_clear_cache('read_environment')

    # return cc, to be populated in template
    return cc




