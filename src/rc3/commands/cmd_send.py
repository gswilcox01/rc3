import copy
import json
import os
import re
from json import JSONDecodeError

import click
import requests
from jsonpath_ng import parse
from requests.auth import HTTPBasicAuth, AuthBase
from requests.exceptions import SSLError

from rc3.commands import cmd_request
from rc3.common import json_helper, print_helper, env_helper, inherit_helper, rc_globals, file_helper, decorators


@click.command("send", short_help="Sends an HTTP request & writes results to a response file.")
@click.option('-p', '--pick', is_flag=True, default=False, help="Pick a REQUEST then send it.")
@click.option('-e', '--edit', is_flag=True, default=False, help="Edit a REQUEST then send it.")
@click.option('-f', '--file', type=click.Path(exists=True, readable=True, allow_dash=True, dir_okay=False), help="File to send as REQUEST body.")
@click.argument('request_name', type=str, required=False, nargs=-1)
def cli(pick, edit, file, request_name):
    """\b
    Will send an HTTP request using the Python requests library.
    \b
    REQUEST_NAME(s) is optional.
    REQUEST_NAME(s) will default to the current_request.
    REQUEST_NAME(s) if used should be one of:
    1. The NUM column from 'rc request --list' output
    2. THe NAME column from 'rc request --list' output

    \b
    OUTPUT will be the response body to STDOUT.
    OUTPUT will also be a *.response file in the same dir as the *.request file.
    """
    if len(request_name) > 1:
        if pick:
            raise click.ClickException("--pick option is invalid if multiple REQUEST_NAMES")
        if edit:
            raise click.ClickException("--edit option is invalid if multiple REQUEST_NAMES")
        if file is not None:
            raise click.ClickException("--file option is invalid if multiple REQUEST_NAMES")
        for name in request_name:
            r = lookup_request(name)
            # make a deepcopy, in case we are sending multiples of the same request, env var subs happen again!
            # & bust the read_env cache, so 2nd request can see extracted values from 1st request
            r = copy.deepcopy(r)
            decorators.rc_clear_cache('read_environment')
            send(r, None)
        return

    # otherwise 0 or 1 request_names
    name = None
    if len(request_name) == 1:
        name = request_name[0]

    if pick and edit:
        r = cmd_request.pick_request(name)
        r = cmd_request.edit_request(None, wrapper=r)
        send(r, file)
    elif pick:
        r = cmd_request.pick_request(name)
        send(r, file)
    elif edit:
        r = cmd_request.edit_request(name)
        send(r, file)
    else:
        r = lookup_request(name)
        send(r, file)


def lookup_and_send(request_name):
    r = lookup_request(request_name)
    send(r, None)


def lookup_request(request_name):
    r = cmd_request.lookup_request(request_name)
    if r is None and request_name is None:
        raise click.ClickException("There is no current REQUEST, exiting...")
    if r is None:
        raise click.ClickException("REQUEST '{}' not found. See 'rc request --list'".format(request_name))
    return r


def send(wrapper, file):
    settings = json_helper.read_settings()
    request = wrapper.get('_original')
    headers = request.get('headers', {})

    # find_auth() before var subs, so env var subs happen in inherited auth also!
    # IMPORTANT! preprocess_file_option() before env var subs, so {{#file}} helper can consume --file if necc.
    request['auth'] = inherit_helper.find_auth(wrapper)
    file_helper.preprocess_file_option(file)
    env_helper.process_subs(wrapper)

    # determine BODY to POST/PUT
    # potentially updates default headers
    # potentially overrides .request settings with --file passed in
    _json, _data = determine_body(request, file, headers)

    timeout = settings.get('request_timeout', 30)
    allow_redirects = settings.get('follow_redirects', False)
    verify = settings.get('ca_cert_verification', True)
    if verify and len(settings.get('ca_bundle','')) > 0:
        verify = settings.get('ca_bundle')
        if not os.path.exists(verify):
            raise click.ClickException(f'settings.json ca_bundle file [{verify}] does not exist!')
    if settings.get('headers_send_nocache', True):
        if 'Cache-Control' not in headers:
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


def determine_body(request, file, headers):
    # --file option overrides all other definitions in .request file
    # IMPORTANT!: file_helper.preprocess_file_option(file) MUST have already been called before handlebar substitution!
    # IMP2: if the --file was consumed by a handlebar expression of "{{ #file }}" already, then it won't be used here!
    if file_helper.state['has_file'] and not file_helper.state['consumed']:
        return file_helper.state['_json'], file_helper.state['_text']

    # no --file option, error if multiple bodies defined
    _json = None
    _data = None
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
        # don't overwrite header if explicitly defined in the .request
        if 'Content-Type' not in headers:
            headers['Content-Type'] = "text/plain"
    elif form_data is not None:
        _data = form_data
    return _json, _data


def process_output(wrapper, response):
    settings = json_helper.read_settings()
    cli_options = rc_globals.get_cli_options()
    request = wrapper.get('_original')

    # process potential extract, and update env file
    extract_buffer = process_extracts(request, response)
    verbose_output = extract_buffer['verbose_output']   # will also have extract_errors & extracted now

    # write out *.response file
    save_responses = request.get('save_responses', settings.get('save_responses', True))
    if save_responses:
        response_filename = os.path.join(wrapper.get('_dir'),
                                         wrapper.get('_filename').split('.')[0] + ".response")
        json_helper.write_json(response_filename, verbose_output)

    # if extracted to STDOUT that overrides everything
    # otherwise print verbose or just response.body
    if len(extract_buffer['stdout']) > 0:
        print_helper.print_json(extract_buffer['stdout'])
    elif cli_options.get('verbose', False):
        print_helper.print_json(verbose_output)
    else:
        print_helper.print_json_or_text(response)


def process_extracts(request, response):
    # env extracts will go straight to the env, but other "to"s and errors collected here
    verbose_output = create_verbose_output(response)
    verbose_output['extract_errors'] = []
    verbose_output['extracted'] = {}
    extract_buffer = {
        "stdout": {},
        "verbose_output": verbose_output,
        "response": verbose_output['extracted'],    # pointer here for easier ref
        "errors": verbose_output['extract_errors']  # pointer here for easier ref
    }

    # do nothing if no "extract" in the request
    extract_list = request.get("extract", None)
    if extract_list is None or len(extract_list) == 0:
        return extract_buffer

    for extract in extract_list:
        process_one_extract(extract, response, extract_buffer)
    return extract_buffer


def process_one_extract(extract, response, extract_buffer):
    to_environment = False
    to = extract.get("to", "global")
    if to in ["global", "current"]:
        to_environment = True
        env_filename, env = json_helper.read_environment(to)

    value = None
    if "json_path" in extract:
        value = extract_json_path(extract, response, extract_buffer)
    elif "text_pattern" in extract:
        value = extract_regex(extract, response, extract_buffer)

    # write to environment if that is the output
    # otherwise write to the buffer where we are collecting 1..n extracts
    var = extract.get("var", "token")
    # print(f'var={var} value={value} to={to}')
    if to_environment:
        env[var] = value
        json_helper.write_environment(env_filename, env)
    elif to == "stdout":
        extract_buffer.get("stdout")[var] = value
    elif to == "response":
        extract_buffer.get("response")[var] = value
    else:
        raise click.ClickException(f"Unrecognized $.extract.to ({to}), please check your .request")


def extract_json_path(extract, response, extract_buffer):
    # attempt to find json path
    # See: https://www.digitalocean.com/community/tutorials/python-jsonpath-examples
    # See: https://jsonpath.com/
    # See: https://pypi.org/project/jsonpath-ng/
    json_path = extract.get("json_path", None)
    errors = extract_buffer['errors']

    # body=response.body, response=verbose_output
    extract_from = extract.get("from", "body")
    target = extract_body_as_json(response) if extract_from == "body" else extract_buffer['verbose_output']
    if target is None:
        errors.append("REQUEST has $.extract.json_path, but response is not JSON!")
        return

    jsonpath_expression = parse(json_path)
    match = jsonpath_expression.find(target)
    if len(match) < 1:
        errors.append("REQUEST json_path=[{}] had no matches in response JSON!".format(json_path))
        return
    # use the value from the first match
    return match[0].value


def extract_regex(extract, response, extract_buffer):
    # See python regex docs here for valid regex patterns:
    # https://docs.python.org/3/howto/regex.html
    text_pattern = extract.get("text_pattern", None)
    errors = extract_buffer['errors']

    # body=response.body, response=verbose_output
    extract_from = extract.get("from", "body")
    target = response.text if extract_from == "body" else print_helper.get_json_string(extract_buffer['verbose_output'])
    if len(target) < 1 and extract_from == "body":
        errors.append("REQUEST has $.extract.text_pattern, but response.text is 0 length!")
        return
    if "(" not in text_pattern or ")" not in text_pattern:
        errors.append("REQUEST $.extract.text_pattern, MUST contain a matching group ()!")
        return

    # do it
    pattern = re.compile(text_pattern)
    match = pattern.search(target)
    # group(0) is the WHOLE match, (1) is the first group in the pattern (what we want)
    if match is None:
        errors.append("REQUEST text_pattern=[{}] had no matches in response JSON!".format(text_pattern))
        return
    return match.group(1)


def extract_body_as_json(response):
    try:
        _json = response.json()
        return _json
    except BaseException as error:
        return None


def create_verbose_output(response):
    body = {}
    if extract_body_as_json(response) is None:
        body['text'] = response.text
    else:
        body['json'] = extract_body_as_json(response)

    headers = {}
    header_size = 0
    for key, value in response.headers.items():
        header_size += len(key) + len(value)
        headers[key.lower()] = value

    # verbose output
    return {
        "status_code": response.status_code,
        "time": str(divmod(response.elapsed.microseconds, 1000)[0]) + "ms",
        # "time2": str(response.elapsed.microseconds / 1000) + "ms",
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
