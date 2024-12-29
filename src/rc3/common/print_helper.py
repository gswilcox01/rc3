import errno
import json
import socket
import sys

import click

from rc3.common import json_helper


def get_json_string(_dict):
    settings = json_helper.read_settings()
    indent = settings.get('indent', 4)
    indent_type = settings.get('indent_type', "space")
    indent_value = indent
    if indent_type == "tab" and indent > 0:
        indent_value = '\t' * indent
    if indent < 0:
        json_string = json.dumps(_dict)
    else:
        json_string = json.dumps(_dict, indent=indent_value)
    return json_string


def extract_json_string(incoming):
    json_string = incoming[incoming.index("{"):]
    return json_string


def print_json(_dict, err=False):
    json_string = get_json_string(_dict)
    if err:
        print(json_string, file=sys.stderr)
    else:
        print(json_string)


def print_json_or_text(response):
    try:
        _dict = response.json()
        print_json(_dict)
    except socket.error as e:
        if e.errno != errno.EPIPE:
            print_text(response)
        # ignore broken pipes


def print_text(response):
    try:
        if len(response.text) == 0:
            print("Status: " + str(response.status_code))
            print("No response body.")
        else:
            print(response.text)
    except socket.error as e:
        if e.errno != errno.EPIPE:
            raise
        # ignore broken pipes


def left_format(_list, field, header_len):
    # max_len = max(len(str(obj[field])) for obj in _list)
    max_len = max(len(str(obj.get(field,"-"))) for obj in _list)
    max_len = max(max_len, header_len)
    this_format = '{:<' + str(max_len + 3) + '}'
    return this_format


def print_formatted_table(header, fields, _list):
    # Create line_format based on MAX WIDTH of each field we are printing
    line_format = ""
    for idx, field in enumerate(fields):
        header_len = len(header[idx])
        line_format += left_format(_list, field, header_len)

    # print header & then each row in the list
    print(line_format.format(*header))
    for row in _list:
        # first convert into a list of values (instead of a dict/object)
        new_row = []
        for field in fields:
            new_row.append(row.get(field, "-"))
        # then print it
        print(line_format.format(*new_row))
