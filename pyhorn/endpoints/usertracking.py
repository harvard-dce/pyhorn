__author__ = 'jluker'

from base import Endpoint, EndpointObj
from episode import EpisodeEndpoint, Episode

class UserTrackingEndpoint(Endpoint):

    _kwarg_map = {
        'user_actions': {
            'type': None,
            'day': None,
            'start': None,
            'end': None,
            'limit': 0,
            'offset': None
        }
    }

    @classmethod
    def user_actions(cls, client, **kwargs):
        params = cls.map_kwargs_to_params('user_actions', kwargs)
        resp_data = client.get('usertracking/actions.json', params)
        if 'action' not in resp_data['actions']:
            return []
        actions = resp_data['actions']['action']
        if isinstance(actions, dict):
            return [actions]
        return actions

class UserSession(EndpointObj):
    pass

class UserAction(EndpointObj):

    @property
    def episode(self):
        return self._ref_property("episode", endpoint_method=EpisodeEndpoint.episode,
                                   endpoint_params={'episode_id': self.mediapackageId},
                                   class_=Episode, single=True)

    @property
    def session(self):
        return self._ref_property("session", path_key="sessionId",
                                  class_=UserSession, single=True)

