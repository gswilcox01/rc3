import os
import re

import click

from rc3.commands import cmd_request
from rc3.common import json_helper, print_helper


@click.command("list", short_help="List collections, envs, requests.")
@click.argument('_type', type=str, required=False)
def cli(_type):
    """\b
    Defaults to listing all collections, and envs & requests in the current_collection

    \b
    TYPE is optional.
    And if supplied should be 1 of:
    1. collections, c
    2. environments, e
    3. requests, r
    """

    if _type is None or re.match('^all', _type, re.I):
        list_collections()
        list_environments()
        list_requests()
    elif re.match('^c', _type, re.I):
        list_collections()
    elif re.match('^e', _type, re.I):
        list_environments()
    elif re.match('^r', _type, re.I):
        list_requests()


def list_collections():
    _list = json_helper.read_collection_list()

    if len(_list) == 0:
        raise click.ClickException("No COLLECTIONS found in settings.json")
    click.echo("Listing COLLECTIONS found in settings.json:")

    # now display table
    header = ['NUM:', 'NAME:', 'LOCATION:']
    fields = ['display_num', 'name', 'location']
    print_helper.print_formatted_table(header, fields, _list)


def list_environments():
    _list = json_helper.read_environment_list()

    if len(_list) == 0:
        raise click.ClickException("No ENVIRONMENTS found in current_collection")
    click.echo("Listing ENVIRONMENTS found in current_collection:")

    # now display table
    header = ['NUM:', 'NAME:', 'baseUrl:']
    fields = ['display_num', 'name', 'baseUrl']
    print_helper.print_formatted_table(header, fields, _list)


def list_requests():
    _list = json_helper.read_request_list()

    if len(_list) == 0:
        raise click.ClickException("No REQUESTS found in current_collection")
    click.echo("Listing REQUESTS found in current_collection:")

    # now display table
    header = ['NUM:', 'FOLDER:', 'METHOD:', 'NAME:']
    fields = ['display_num', 'folder', 'method', 'name']
    print_helper.print_formatted_table(header, fields, _list)

