import json
import os
import time

import click
import jwt
from click import ClickException

from rc3.commands import cmd_list
from rc3.common import json_helper, print_helper, config_helper, env_helper
from rc3.common.data_helper import SCHEMA_BASE_URL, SCHEMA_PREFIX, SCHEMA_VERSION


@click.command("decode", short_help="Decode a JWT stored in an ENV or KEYRING.")
@click.argument('jwt_var', type=str, required=False)
def cli(jwt_var):
    """\b
    Will attempt to decode the JWT_VAR from the current or global environment, or keyring.
    If no JWT_VAR argument is passed will attempt to decode the 'token' var name.

    """
    var = 'token' if jwt_var is None else jwt_var
    try:
        value = env_helper.lookup_one_var(var)
    except ClickException:
        raise click.ClickException(f"No ENV VAR found for [{var}]")
    if value is None:
        raise click.ClickException(f"No ENV VAR found for [{var}]")

    try:
        headers = jwt.get_unverified_header(value)
        payload = jwt.decode(value, options={"verify_signature": False})
    except jwt.exceptions.DecodeError as error:
        raise click.ClickException(f"There was an error decoding the JWT in ENV VAR [{var}]\n{error}")
        # print(error)

    print(f'Decoding HEADERS and CLAIMS from \'{var}\' env var')
    print_helper.print_json(headers)
    print_helper.print_json(payload)
    if 'iat' in payload:
        iat = payload['iat']
        print(f'Issued at:  {time.ctime(iat)}')
    if 'exp' in payload:
        exp = payload['exp']
        now = time.time()
        if exp < now:
            click.echo(click.style(f'Expired at: {time.ctime(exp)}', fg='red'))
            print(f'Curr time:  {time.ctime(time.time())}')
        else:
            print(f'Curr time:  {time.ctime(time.time())}')
            click.echo(click.style(f'Expires at: {time.ctime(exp)}', fg='green'))
