
import arrow
from .base import Endpoint, EndpointObj
from .search import SearchEndpoint, SearchEpisode

__all__ = ['UserTrackingEndpoint', 'UserAction']

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

class UserAction(EndpointObj):

    @property
    def episode(self):
        return self._ref_property("episode", endpoint_method=SearchEndpoint.episode,
                                   endpoint_params={'episode_id': self.mediapackageId},
                                   class_=SearchEpisode, single=True)


    def is_live(self):
        """
        Assumes that the mediapackage.start would represent the start time of a
         live recording. Therefore, if the creation of the user action occurs
         prior to the start + the duration then it must be a live-viewing event
        """
        action_created = arrow.get(self.created)
        mp_start = arrow.get(self.episode.mediapackage.start)
        mp_duration_sec = int(self.episode.mediapackage.duration) / 1000
        return action_created <= mp_start.replace(seconds=+mp_duration_sec)
