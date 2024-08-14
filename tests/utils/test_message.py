from mcq_bot.utils.message import extract_command_content


def test_extract_command_content():
    text = "/start my extracted text"
    assert extract_command_content(text) == "my extracted text"
    assert extract_command_content("/emptycommand") is None
