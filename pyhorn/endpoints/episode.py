
from base import Endpoint, EndpointObj
from urlparse import urljoin
from urllib import quote

__all__ = ['EpisodeEndpoint', 'Episode', 'Mediapackage', 'MediaTrack']

class EpisodeEndpoint(Endpoint):

    _kwarg_map = {
        'episode': {
            'format': 'json',
            'id': None,
            'q': None,
            'creator': None,
            'contributor': None,
            'language': None,
            'series': None,
            'license': None,
            'title': None,
            'limit': 10,
            'offset': 0,
            'sort': None,
            'onlyLatest': True
        }
    }

    @classmethod
    def episodes(cls, client, **kwargs):
        params = cls.map_kwargs_to_params('episode', kwargs)
        resp_data = client.get('/episode/episode.json', params)
        if 'result' not in resp_data['search-results']:
            return []
        eps = resp_data['search-results']['result']
        if isinstance(eps, dict):
            return [eps]
        return eps

    @classmethod
    def episode(cls, client, episode_id):
        ep_search = EpisodeEndpoint.episodes(client, id=episode_id)
        if len(ep_search) == 0:
            return None
        return ep_search[0]

class MediaTrack(EndpointObj):
    pass

class Mediapackage(EndpointObj):

    def __repr__(self):
        return "Mediapackage %s" % self.id

    @property
    def tracks(self):
        return self._ref_property('tracks', path_key="media.track",
                                   class_=MediaTrack)

class Episode(EndpointObj):

    def __repr__(self):
        return "Episode %s" % self.id

    @property
    def url(self):
        return urljoin(self.client.base_url,
                        "episode/episode.json?id=%s" % quote(self.id))

    @property
    def mediapackage(self):
        return self._ref_property('mediapackage', path_key='mediapackage',
                                       class_=Mediapackage, single=True)

