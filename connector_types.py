from core_utils.logger import logger

from exception import RemoteError
from output_types import CmdOutput
import re


class ToxidoObject(object):
    _SUCCESS_CREATE_CMD_OUT = "SUCCESS_CREATE_CMD"
    _IDENTIFIER = "0x1234567890"
    _TOXIDO_SOCK_TIMEOUT = 180
    _EOL = "\x03\x03\x03"
    _OUTPUT_REGEX = "((?:1)|(?:2)) (.*)\x03\x03\x03"
    COMMAND_TEMPLATE = "{command}\x03\x03{arg}" + _EOL
    _SUCCESS_CLOSE_CMD_OUT = "SUCCESS_CLOSE_CMD"
    STD_STR = {1: "OUTPUT", 2: "ERROR"}

    def __init__(self, ssl_sock):
        self._sock = ssl_sock
        self._sock.set_timeout(self._TOXIDO_SOCK_TIMEOUT)
        self._host, self._port = self._get_connection_info()
        self._logger = logger.getLogger("{0},{1}:{2}".format(self.__class__, self._host, self._port))
        self.init()

    def __repr__(self):
        return "<{name},{ip}>".format(name="ToxidoClient", ip=self._host)

    def init(self):
        std, identifier = self.recv_refined_data()
        if std == 'OUTPUT' and identifier != self._IDENTIFIER:
            self._logger.warn("computer connect but not identified correctly")
        elif std == 'ERROR':
            RemoteError("ERROR: {0}".format(identifier))

    def run_commandline(self, input_cmd):

        output = self._get_cmd_output(input_cmd)
        return CmdOutput(output)

    def recv_refined_data(self):
        raw_data = self._sock.recv_data()
        next_data = raw_data
        while self._EOL not in next_data:
            next_data = self._sock.recv_data()
            raw_data += next_data

        std, data = m = re.match(self._OUTPUT_REGEX, raw_data, re.S).groups()
        return self.STD_STR[int(std)], data

    def _send_command(self, command, arg):
        self._sock.send_data(self.COMMAND_TEMPLATE.format(command=command, arg=arg))

    def close(self):
        self._sock.shutdown()
        self._sock.close()

    def open_cmd(self):
        self._send_open_cmd_command()

    def close_cmd(self):
        self._send_close_cmd_command()

    def _send_open_cmd_command(self):
        self._send_command("CMD_OPEN", "")
        std, output = self.recv_refined_data()
        if std != 'OUTPUT' and output != self._SUCCESS_CREATE_CMD_OUT:
            raise RemoteError("CMD_CREATION_FAILED: {0}".format(output))

    def _get_cmd_output(self, input_cmd):
        self._send_cmd_input_command(input_cmd)
        std, data = self.recv_refined_data()
        if std == 'OUTPUT':
            return data
        RemoteError("Failed to get cmd output: {0}".format(data))

    def _send_cmd_input_command(self, input_cmd):
        self._send_command("CMD_IN", input_cmd)

    def _get_connection_info(self):
        return self._sock._sock.getpeername()

    def _send_close_cmd_command(self):
        self._send_command("CMD_CLOSE", "")
        std, output = self.recv_refined_data()
        if std == 'ERROR':
            raise RemoteError("CMD_CLOSING_FAILED: {0}".format(output))
