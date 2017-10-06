
from .base import Endpoint

__all__ = ['InfoEndpoint']

class InfoEndpoint(Endpoint):

    @classmethod
    def endpoints(class_, client):
        components = class_.components(client)
        return components.get('rest', [])

    @classmethod
    def components(class_, client):
        """
        :param client: instance of client.MHClient
        :return: data parsed from json response
        """
        return client.get('info/components.json')

    @classmethod
    def me(class_, client):
        """
        :param client: instance of client.MHClient
        :return: data parsed from json response
        """
        return client.get('info/me.json')

