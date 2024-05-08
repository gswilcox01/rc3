import os
import re

import click
import requests
from jsonpath_ng import parse
from requests.auth import HTTPBasicAuth, AuthBase
from requests.exceptions import SSLError

from rc3.commands import cmd_request
from rc3.common import json_helper, print_helper, env_helper, inherit_helper, rc_globals


@click.command("send", short_help="Sends an HTTP request & writes results to a response file.")
@click.option('-p', '--pick', is_flag=True, default=False, help="Pick a REQUEST then send it.")
@click.option('-e', '--edit', is_flag=True, default=False, help="Edit a REQUEST then send it.")
@click.argument('request_name', type=str, required=False)
def cli(pick, edit, request_name):
    """\b
    Will send an HTTP request using the Python requests library.
    \b
    REQUEST_NAME is optional.
    REQUEST_NAME will default to the current_request.
    REQUEST_NAME if used should be one of:
    1. The NUM column from 'rc request --list' output
    2. THe NAME column from 'rc request --list' output

    \b
    OUTPUT will be the response body to STDOUT.
    OUTPUT will also be a *.response file in the same dir as the *.request file.
    """
    if pick and edit:
        r = cmd_request.pick_request(request_name)
        r = cmd_request.edit_request(None, wrapper=r)
        send(r)
    elif pick:
        r = cmd_request.pick_request(request_name)
        send(r)
    elif edit:
        r = cmd_request.edit_request(request_name)
        send(r)
    else:
        r = lookup_request(request_name)
        send(r)


def lookup_request(request_name):
    r = cmd_request.lookup_request(request_name)
    if r is None and request_name is None:
        raise click.ClickException("There is no current REQUEST, exiting...")
    if r is None:
        raise click.ClickException("REQUEST '{}' not found. See 'rc request --list'".format(request_name))
    return r


def send(wrapper):
    settings = json_helper.read_settings()
    request = wrapper.get('_original')
    headers = request.get('headers', {})

    # find_auth() before var substitution!
    request['auth'] = inherit_helper.find_auth(wrapper)
    env_helper.process_subs(wrapper)

    body_count = 0
    _json = request.get('body', {}).get('json', None)
    if _json is not None:
        body_count += 1
    text = request.get('body', {}).get('text', None)
    if text is not None:
        body_count += 1
    form_data = request.get('form_data', None)
    if form_data is not None:
        body_count += 1
    if body_count > 1:
        raise click.ClickException("REQUEST can only have 1 of body.json, body.text, or form_data.  You have {}.".format(body_count))

    _data = None
    if text is not None:
        _data = text
        headers['Content-Type'] = "text/plain"
    elif form_data is not None:
        _data = form_data

    timeout = settings.get('request_timeout', 30)
    allow_redirects = settings.get('follow_redirects', False)
    verify = settings.get('ca_cert_verification', True)
    if verify and len(settings.get('ca_bundle','')) > 0:
        verify = settings.get('ca_bundle')
        if not os.path.exists(verify):
            raise click.ClickException(f'settings.json ca_bundle file [{verify}] does not exist!')
    if settings.get('headers_send_nocache', True):
        headers['Cache-Control'] = 'no-cache'

    try:
        response = requests.request(request.get('method'), request.get('url'),
                                    headers=headers,
                                    json=_json,
                                    auth=create_auth(inherit_helper.find_auth(wrapper)),
                                    params=request.get('params', None),
                                    data=_data,
                                    timeout=timeout,
                                    allow_redirects=allow_redirects,
                                    verify=verify)
    except SSLError as e:
        print()
        print(type(e).__name__ + ": " + str(e))
        click.echo("SSLError: Try setting REQUESTS_CA_BUNDLE, CURL_CA_BUNDLE, or rc-settings.ca_bundle")
        click.echo("See: https://github.com/gswilcox01/rc3/tree/master?tab=readme-ov-file#ca-certificates")
        raise click.Abort

    process_output(wrapper, response)


def process_output(wrapper, response):
    settings = json_helper.read_settings()
    cli_options = rc_globals.get_cli_options()
    request = wrapper.get('_original')

    # process potential extract, and update env file
    extract_errors = process_extract(request, response)

    # determine verbose output for console or file
    verbose_output = create_verbose_output(response)
    verbose_output['extract_errors'] = extract_errors

    # write out *.response file
    save_responses = request.get('save_responses', settings.get('save_responses', True))
    if save_responses:
        response_filename = os.path.join(wrapper.get('_dir'),
                                         wrapper.get('_filename').split('.')[0] + ".response")
        json_helper.write_json(response_filename, verbose_output)

    # display either verbose_output OR just the response body
    if cli_options.get('verbose', False):
        print_helper.print_json(verbose_output)
    else:
        print_helper.print_json_or_text(response)


def process_extract(request, response):
    # collect extract errors, and return them for display or storage on .response
    errors = []

    # do nothing if not "extract" in the def
    extract = request.get("extract", None)
    if extract is None:
        return errors

    # sys.exit with error, if env doesn't exist in the collection (or global doesn't exist)
    env_name = extract.get("env", "global")
    env_filename, env = json_helper.read_environment(env_name)

    # default to "token" if var is not set
    var = extract.get("var", "token")

    # attempt to find json path
    # See: https://www.digitalocean.com/community/tutorials/python-jsonpath-examples
    # See: https://jsonpath.com/
    # See: https://pypi.org/project/jsonpath-ng/
    json_path = extract.get("json_path", None)
    if json_path is not None:
        _json = extract_json(response)
        if _json is None:
            errors.append("REQUEST has $.extract.json_path, but response is not JSON!")
            return errors
        jsonpath_expression = parse(json_path)
        match = jsonpath_expression.find(_json)
        if len(match) < 1:
            errors.append("REQUEST json_path=[{}] had no matches in response JSON!".format(json_path))
            return errors
        # use the value from the first match
        value = match[0].value
        env[var] = value
        json_helper.write_environment(env_filename, env)
        return errors

    # See python regex docs here for valid regex patterns:
    # https://docs.python.org/3/howto/regex.html
    text_pattern = extract.get("text_pattern", None)
    if text_pattern is not None:
        text = response.text
        if len(text) < 1:
            errors.append("REQUEST has $.extract.text_pattern, but response.text is 0 length!")
            return errors
        if "(" not in text_pattern or ")" not in text_pattern:
            errors.append("REQUEST $.extract.text_pattern, MUST contain a matching group ()!")
            return errors
        # do it
        pattern = re.compile(text_pattern)
        match = pattern.search(text)
        # group(0) is the WHOLE match, (1) is the first group in the pattern (what we want)
        if match is None:
            errors.append("REQUEST text_pattern=[{}] had no matches in response JSON!".format(text_pattern))
            return errors
        env[var] = match.group(1)
        json_helper.write_environment(env_filename, env)
        return errors


def extract_json(response):
    try:
        _json = response.json()
        return _json
    except BaseException as error:
        return None


def create_verbose_output(response):
    body = {}
    if extract_json(response) is None:
        body['text'] = response.text
    else:
        body['json'] = extract_json(response)

    headers = {}
    header_size = 0
    for key, value in response.headers.items():
        header_size += len(key) + len(value)
        headers[key] = value

    # verbose output
    return {
        "status_code": response.status_code,
        "time": str(response.elapsed.microseconds / 1000) + "ms",
        "size": {
            "body": len(response.content),
            "headers": header_size,
            "total": len(response.content) + header_size
        },
        "headers": headers,
        "body": body
    }


class HTTPTokenAuth(AuthBase):
    def __init__(self, token, token_header="Authorization", token_name="Bearer"):
        self.token = token
        self.token_header = token_header
        self.token_name = token_name

    def __call__(self, r):
        value = self.token_name + " " + self.token
        r.headers[self.token_header] = value.strip()
        return r


def create_auth(auth_config):
    _auth = None
    _type = auth_config.get('type')
    if _type == 'basic':
        _auth = HTTPBasicAuth(auth_config.get('username'), auth_config.get('password'))
    if _type == 'bearer':
        _auth = HTTPTokenAuth(auth_config.get('bearer_token'))
    if _type == 'token':
        _auth = HTTPTokenAuth(auth_config.get('token_value'),
                              token_name="",
                              token_header=auth_config.get('token_header', "Authorization"))
    return _auth
