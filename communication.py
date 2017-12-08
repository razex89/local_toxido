from core_utils.session.session import SSLServer
from connector_types import ToxidoObject


class LocalCommunicator(SSLServer):

    def wait_and_get_toxido(self, seconds=None):
        self.set_timeout(seconds)
        ssl_sock = self.accept()
        tox_obj = ToxidoObject(ssl_sock)
        tox_obj._logger.info("connected to a toxido!")
        return tox_obj





