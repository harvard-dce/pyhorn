__author__ = 'jluker'

class Endpoint(object):
    pass

class Info(Endpoint):

    @staticmethod
    def components(client):
        return client.get('/info/components.json')

    @staticmethod
    def me(client):
        return client.get('/info/me.json')

class UserTracking(Endpoint):

    @staticmethod
    def actions(client, **kwargs):
        params = kwargs
        _actions = client.get('/usertracking/actions.json', params)
