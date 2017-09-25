# Standard library imports
import atexit
import socket

# Third-party imports
import requests

# Local imports
from uplink import utils


class RequestsSessionFactory(object):

    def __init__(self):
        self.__ip_cache = {}

    @staticmethod
    def _get_host(url):
        parsed_url = utils.urlparse.urlparse(url)
        return socket.gethostbyname(parsed_url.netloc)

    @staticmethod
    def _create_requests_session():
        session = requests.Session()
        atexit.register(session.close)
        return session

    def __call__(self, domain):
        host = self._get_host(domain)
        if host not in self.__ip_cache:
            self.__ip_cache[host] = self._create_requests_session()
        return self.__ip_cache[host]


class RequestsBackend(object):
    _session_factory = RequestsSessionFactory()

    def send_request(self, method, url, extras):
        session = self._session_factory(url)
        return session.request(
            method=method,
            url=url,
            **extras
        )
