import os
import re

import click
import requests
from jsonpath_ng import parse
from requests.auth import HTTPBasicAuth, AuthBase

from rc3.commands import cmd_request
from rc3.common import json_helper, print_helper, env_helper, inherit_helper


@click.command("subs", short_help="Temp test subs.")
@click.option('-p', '--pick', is_flag=True, default=False, help="Pick a REQUEST then sub it.")
@click.argument('request_name', type=str, required=False)
def cli(pick, request_name):
    """\b
    Will sub an REQUEST object.
    """
    if pick:
        r = cmd_request.pick_request()
        inherit_helper.find_auth(r)
        # env_helper.process_subs(r)
    else:
        r = lookup_request(request_name)
        inherit_helper.find_auth(r)
        # env_helper.process_subs(r)


def lookup_request(request_name):
    r = cmd_request.lookup_request(request_name)
    if r is None and request_name is None:
        raise click.ClickException("There is no current REQUEST, exiting...")
    if r is None:
        raise click.ClickException("REQUEST '{}' not found. See 'rc request --list'".format(request_name))
    return r
