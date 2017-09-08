from core_utils.session.session import SSLServer
from connector_types import ToxidoObject


class LocalCommunicator(SSLServer):

    def wait_and_get_toxido(self, seconds=None):
        self.set_timeout(seconds)
        ssl_sock = self.accept()
        tox_obj = ToxidoObject(ssl_sock)
        tox_obj._logger.log("connected to a toxido!", tox_obj._logger.Level.INFO)
        return tox_obj





