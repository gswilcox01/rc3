import re

from rc3.common import print_helper


def test_formatted_table(capsys):
    header = ['IDENTIFIER:', 'NAME:']
    fields = ['id', 'name']
    _list = [
        {'id': 1, 'name': 'gary'},
        {'id': 2, 'name': 'bob maloney'}
    ]

    print_helper.print_formatted_table(header, fields, _list)
    captured = capsys.readouterr()
    assert re.match(r'IDENTIFIER.+\n1.+gary.+\n2.+bob maloney', captured.out)
