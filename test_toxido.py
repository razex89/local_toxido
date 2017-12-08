import pytest
from communication import LocalCommunicator


def test_local_toxido():
    l = LocalCommunicator("127.0.0.1", 9999)
    t = l.wait_and_get_toxido(30)
    t.open_cmd()
    assert t.run_commandline("whoami")._text == "razpc\\raz\r\n"
    t.close_cmd()
    t.close()
    l.close()

