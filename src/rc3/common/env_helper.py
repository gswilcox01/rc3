import json
import os
import re
import click

from rc3.common import json_helper, print_helper


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


def lookup_var_value(envs, var):
    for env in envs:
        if var in env:
            return env.get(var)
    raise click.ClickException(f'var {{{{{var}}}}} is in the REQUEST but cannot be found in the current, global, or OS environment')


def sub_in_dict(envs, d):
    if d is None:
        return
    pattern = re.compile(r'{{(.*?)}}')
    for key, value in d.items():
        new_value = value
        for match in pattern.finditer(value):
            var = match.group(1).strip()
            var_value = lookup_var_value(envs, var)
            # this allows multiple vars to be used in a single value (each gets replaced)
            new_value = new_value.replace(match.group(0), var_value)
        d[key] = new_value


def sub_in_string(envs, s):
    if s is None:
        return None
    pattern = re.compile(r'{{(.*?)}}')
    for match in pattern.finditer(s):
        var = match.group(1).strip()
        var_value = lookup_var_value(envs, var)
        s = s.replace(match.group(0), var_value)
    return s


def has_vars(wrapper):
    r = wrapper.get('_original')
    dicts = [
        r.get('form_data',{}),
        r.get('headers',{}),
        r.get('params',{}),
        r.get('auth',{})
    ]
    strings = [
        r.get('url',''),
        r.get('body', {}).get('text',''),
        json.dumps(r.get('body', {}).get('json',{}))
    ]
    for d in dicts:
        for v in d.values():
            strings.append(v)

    pattern = re.compile(r'{{(.*?)}}')
    for s in strings:
        match = pattern.search(s)
        if match is not None:
            return True
    return False
