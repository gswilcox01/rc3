from rc3.common import file_helper


def test_text_content(text_file):
    content = text_file.read_text()
    assert content == "Hello, World!"


def test_json_content(json_file):
    content = json_file.read_text()
    assert "Koar" in content


def test_preprocess_json(json_file):
    file_helper.preprocess_file_option(json_file)
    s = file_helper.consume_as_string()
    assert "Koar" in s
    assert file_helper.state['has_file'] is True
    assert file_helper.state['consumed'] is True
    assert file_helper.state['_json'] is not None
    assert file_helper.state['_text'] is None


def test_preprocess_text(text_file):
    file_helper.preprocess_file_option(text_file)
    s = file_helper.consume_as_string()
    assert "Hello" in s
    assert file_helper.state['has_file'] is True
    assert file_helper.state['consumed'] is True
    assert file_helper.state['_json'] is None
    assert file_helper.state['_text'] is not None
