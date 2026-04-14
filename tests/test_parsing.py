from services.parsing import is_probable_youtube_url, parse_user_input


def test_parse_pipe_filename():
    parsed = parse_user_input("https://example.com/video.mp4|custom.mp4")

    assert parsed.source_url == "https://example.com/video.mp4"
    assert parsed.custom_file_name == "custom.mp4"


def test_parse_pipe_auth():
    parsed = parse_user_input("https://example.com/file|name|user|pass")

    assert parsed.username == "user"
    assert parsed.password == "pass"


def test_parse_star_filename():
    parsed = parse_user_input("https://example.com/video.mp4 * renamed.mp4")

    assert parsed.custom_file_name == "renamed.mp4"


def test_detect_youtube_url():
    assert is_probable_youtube_url("https://youtu.be/test")
    assert is_probable_youtube_url("https://www.youtube.com/watch?v=test")
