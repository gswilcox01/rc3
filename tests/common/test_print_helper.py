import re

from rc3.common import print_helper, file_helper, json_helper


def test_formatted_table(capsys):
    header = ['IDENTIFIER:', 'NAME:']
    fields = ['id', 'name']
    _list = [
        {'id': 1, 'name': 'gary'},
        {'id': 2, 'name': 'bob maloney'}
    ]

    print_helper.print_formatted_table(header, fields, _list)
    captured = capsys.readouterr()
    match = re.search(r'IDENTIFIER.+\n1(.+)gary.+\n2(.+)bob maloney', captured.out)
    assert match is not None
    g1 = match.group(1)
    g2 = match.group(2)
    assert g1 == g2
    assert g1 == " " * 13


def test_format_settings(example_collection, json_file):
    _dict = file_helper.read_as_json(json_file)
    settings = json_helper.read_settings()

    s = print_helper.get_json_string(_dict)
    assert settings.get('indent') == 4
    assert '    "text"' in s
    assert '    "language"' in s
    assert s.count("\n") == 3

    settings['indent'] = 2
    json_helper.write_settings(settings)
    s = print_helper.get_json_string(_dict)
    assert '  "text"' in s
    assert '  "language"' in s
    assert s.count("\n") == 3

    settings['indent'] = -1
    json_helper.write_settings(settings)
    s = print_helper.get_json_string(_dict)
    assert '{"text"' in s
    assert ', "language"' in s
    assert s.count("\n") == 0

    settings['indent'] = 3
    settings['indent_type'] = "tab"
    json_helper.write_settings(settings)
    s = print_helper.get_json_string(_dict)
    assert '\t\t\t"text"' in s
    assert '\t\t\t"language"' in s
    assert s.count("\n") == 3


def test_extract(example_collection, json_file):
    _dict = file_helper.read_as_json(json_file)
    s1 = print_helper.get_json_string(_dict)
    s2 = "   " + s1
    s3 = print_helper.extract_json_string(s2)
    assert s1 == s3
    assert s1 != s2


def test_print_out(example_collection, json_file, capsys):
    _dict = file_helper.read_as_json(json_file)
    print_helper.print_json(_dict)
    captured = capsys.readouterr()
    assert '    "text"' in captured.out
    assert captured.err == ''


def test_print_err(example_collection, json_file, capsys):
    _dict = file_helper.read_as_json(json_file)
    print_helper.print_json(_dict, err=True)
    captured = capsys.readouterr()
    assert '    "text"' in captured.err
    assert captured.out == ''
