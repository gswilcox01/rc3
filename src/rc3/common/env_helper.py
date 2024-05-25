import json
import os
import re
import click

from rc3.common import json_helper, print_helper

PATTERN = re.compile(r'{{(.*?)}}')


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
        new_string = sub_in_string(envs, json_string)
        if new_string != json_string:
            r.get('body')['json'] = json.loads(new_string)


def lookup_var_value(envs, var, seen=None):
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
