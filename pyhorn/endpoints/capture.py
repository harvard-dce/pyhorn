
import six
from .base import Endpoint, EndpointObj
from .cache import cached

if six.PY3:
    from urllib.parse import urljoin, quote
else:
    from urllib import quote
    from urlparse import urljoin

__all__ = ['CaptureEndpoint', 'CaptureAgent']

class CaptureEndpoint(Endpoint):

    _kwarg_map = {}

    @classmethod
    def agents(cls, client):
        resp_data = client.get('/capture-admin/agents.json')
        if not isinstance(resp_data['agents'], dict) \
                or "agent" not in resp_data['agents']:
            return []
        agents = resp_data['agents']['agent']
        if isinstance(agents, dict):
            return [agents]
        return agents

    @classmethod
    @cached(ttl=30)
    def agent(cls, client, agent_name):
        resp_data = client.get('/capture-admin/agents/%s.json' % agent_name)
        return resp_data['agent-state-update']


class CaptureAgent(EndpointObj):

    def __repr__(self):
        return "Capture Agent %s" % self.name

    @property
    def url(self):
        return urljoin(self.client.base_url,
                        "capture-admin/agents/%s.json" % quote(self.name))

    @property
    def capabilities(self):
        if 'capabilities' in self._property_stash:
            return self._property_stash['capabilities']
        caps = {}
        if isinstance(self._raw['capabilities'], dict):
            for item in self._raw['capabilities']['item']:
                caps[item['key']] = item['value']
        self._property_stash['capabilities'] = caps
        return caps
