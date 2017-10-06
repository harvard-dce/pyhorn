
import six
from .base import Endpoint
from .episode import Episode
from .cache import cached

if six.PY3:
    from urllib.parse import urljoin, quote
else:
    from urllib import quote
    from urlparse import urljoin

__all__ = ['SearchEndpoint', 'SearchEpisode']

class SearchEndpoint(Endpoint):

    _kwarg_map = {
        'episode': {
            'format': 'json',
            'id': None,
            'q': None,
            'sid': None,
            'limit': 10,
            'offset': 0,
            'admin': True,
            'includeDeleted': None,
            'createdFrom': None,
            'createdTo': None,
            'sort': None
        }
    }

    @classmethod
    def episodes(cls, client, **kwargs):
        params = cls.map_kwargs_to_params('episode', kwargs)
        resp_data = client.get('/search/episode.json', params)
        if 'result' not in resp_data['search-results']:
            return []
        eps = resp_data['search-results']['result']
        if isinstance(eps, dict):
            return [eps]
        return eps

    @classmethod
    @cached(ttl=300, max_entries=1000)
    def episode(cls, client, episode_id):
        ep_search = SearchEndpoint.episodes(client, id=episode_id)
        if len(ep_search) == 0:
            return None
        return ep_search[0]

class SearchEpisode(Episode):

    @property
    def url(self):
        return urljoin(self.client.base_url,
                        "search/episode.json?id=%s" % quote(self.id))


