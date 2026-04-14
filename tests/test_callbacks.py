from utils.callbacks import RequestCallback, UiCallback


def test_ui_callback_pack():
    packed = UiCallback(action="help").pack()
    assert packed == "ui:help"


def test_request_callback_pack():
    packed = RequestCallback(token="abc123", action="fmt0").pack()
    assert packed == "req:abc123:fmt0"
