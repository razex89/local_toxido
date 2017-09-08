from core_utils.logger import logger
from output_types import CmdOutput
import re


class ToxidoObject(object):
    _SUCCESS_CREATE_CMD_OUT = "SUCCESS_CREATE_CMD"
    _IDENTIFIER = "0x1234567890"
    _TOXIDO_SOCK_TIMEOUT = 180
    _EOL = "\x03\x03EOLEOLEOL"
    _OUTPUT_REGEX = "OUTPUT (.*)"
    COMMAND_TEMPLATE = "{command}\x03\x03{arg}" + _EOL

    def __init__(self, ssl_sock):
        self._sock = ssl_sock
        self._sock.set_timeout(self._TOXIDO_SOCK_TIMEOUT)
        self._logger = logger
        self._host, self._port = self._get_connection_info()
        self.init()

    def _get_connection_info(self):
        return self._sock._sock.getpeername()

    def recv_refined_data(self):
        data = self._sock.recv_data()
        next_data = data
        while self._EOL not in next_data:
            next_data = self._sock.recv_data()
            data += next_data
        return data[:-1 * len(self._EOL)]

    def _send_command(self, command, arg):
        self._sock.send_data(self.COMMAND_TEMPLATE.format(command=command, arg=arg))

    def init(self):
        identifier = self.recv_refined_data()
        if identifier != self._IDENTIFIER:
            logger.log("computer connect but not identified correctly", logger.Level.WARNING)

    def close(self):
        self._sock.close()

    def __repr__(self):
        return "<{name},{ip}>".format(name="ToxidoClient", ip=self._host)

    def _send_open_cmd_command(self):
        self._send_command("CMD_OPEN", "")
        output = self.recv_refined_data()
        if output != self._SUCCESS_CREATE_CMD_OUT:
            self._logger.log("CMD_CREATION_FAILED: {0}".format(output), logger.Level.CRITICAL)

    def open_cmd(self):
        self._send_open_cmd_command()

    def _get_cmd_output(self, input_cmd):
        self._send_cmd_input_command(input_cmd)
        data = self.recv_refined_data()
        m = re.match(self._OUTPUT_REGEX, data, re.S)
        return m.group(1)

    def _send_cmd_input_command(self, input_cmd):
        self._sock.send_data("CMD_IN\x03\x03{0}\x03\x03EOLEOLEOL".format(input_cmd))

    def run_commandline(self, input_cmd):
        return CmdOutput(self._get_cmd_output(input_cmd))
