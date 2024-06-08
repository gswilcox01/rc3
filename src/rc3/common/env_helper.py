import json
import os
import re
import click

from rc3.common import json_helper, print_helper, helper_functions, decorators

PATTERN = re.compile(r'{{(.*?)}}')
JSON_FILE_PATTERN = re.compile(r'"{{(.*?#file.*?)}}"')


def lookup_one_var(var):
    envs = [
        json_helper.read_environment('current')[1],
        json_helper.read_environment('global')[1],
        os.environ
    ]
    return lookup_var_value(envs, var)


def process_subs(wrapper):
    if has_vars(wrapper):
        sub_vars(wrapper)
    # print_helper.print_json(r.get('_original', None))


def sub_vars(wrapper):
    envs = [
        json_helper.read_environment('current')[1],
        json_helper.read_environment('global')[1],
        os.environ
    ]
    r = wrapper.get('_original')

    # sub dicts
    sub_in_dict(envs, r.get('form_data'))
    sub_in_dict(envs, r.get('headers'))
    sub_in_dict(envs, r.get('params'))
    sub_in_dict(envs, r.get('auth'))

    # sub strings (& json body)
    r['url'] = sub_in_string(envs, r.get('url'))
    text = r.get('body', {}).get('text')
    if text is not None:
        r.get('body')['text'] = sub_in_string(envs, text)
    _json = r.get('body', {}).get('json')
    if _json is not None:
        json_string = json.dumps(_json)
        # special sub for {{ #file }} in JUST the body.json portion of the .request
        new_string = sub_file_in_json_string(envs, json_string)
        new_string = sub_in_string(envs, new_string)
        if new_string != json_string:
            r.get('body')['json'] = json.loads(new_string)


def lookup_var_value(envs, var, seen=None):
    # if var starts with #, then treat is as a helper function and NOT env var
    if var.startswith("#"):
        return helper_functions.lookup_helper_value(var)

    # seen just holds vars that have already seen for THIS lookup
    # if already seen, then we have an infinite loop...
    if seen is None:
        seen = []
    if var in seen:
        raise click.ClickException(
            f'var {{{{{var}}}}} has caused an infinite loop during lookup, please check/update your vars!')
    else:
        seen.append(var)

    for env in envs:
        if var in env:
            outer_value = env.get(var)
            for match in PATTERN.finditer(outer_value):
                inner_var = match.group(1).strip()
                inner_value = lookup_var_value(envs, inner_var, seen)
                outer_value = outer_value.replace(match.group(0), inner_value)
            return outer_value
    raise click.ClickException(
        f'var {{{{{var}}}}} is in the REQUEST but cannot be found in the current, global, or OS environment')


def sub_in_dict(envs, d):
    if d is None:
        return
    # pattern = re.compile(r'{{(.*?)}}')
    for key, value in d.items():
        new_value = value
        for match in PATTERN.finditer(value):
            var = match.group(1).strip()
            var_value = lookup_var_value(envs, var)
            # this allows multiple vars to be used in a single value (each gets replaced)
            new_value = new_value.replace(match.group(0), var_value)
        d[key] = new_value


def sub_file_in_json_string(envs, s):
    if s is None:
        return None
    # JUST for {{ #file }} expressions in json.body, we want to replace surrounding double quotes also!
    # I.E.: "{{ #file }}" and not just {{ #file }}
    # NOTE: if #file is used in other parts of the request, it will do normal subbing, and not replace ""
    for match in JSON_FILE_PATTERN.finditer(s):
        var = match.group(1).strip()
        var_value = lookup_var_value(envs, var)
        s = s.replace(match.group(0), var_value)
    return s


def sub_in_string(envs, s):
    if s is None:
        return None
    # pattern = re.compile(r'{{(.*?)}}')
    for match in PATTERN.finditer(s):
        var = match.group(1).strip()
        var_value = lookup_var_value(envs, var)
        s = s.replace(match.group(0), var_value)
    return s


def has_vars(wrapper):
    r = wrapper.get('_original')
    dicts = [
        r.get('form_data', {}),
        r.get('headers', {}),
        r.get('params', {}),
        r.get('auth', {})
    ]
    strings = [
        r.get('url', ''),
        r.get('body', {}).get('text', ''),
        json.dumps(r.get('body', {}).get('json', {}))
    ]
    for d in dicts:
        for v in d.values():
            strings.append(v)

    # pattern = re.compile(r'{{(.*?)}}')
    for s in strings:
        match = PATTERN.search(s)
        if match is not None:
            return True
    return False
