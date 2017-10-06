"""
pyhorn.client
~~~~~~~~~~~~~~
Defines the main API client class
"""

import os
import six
import requests
from requests.auth import HTTPDigestAuth
from .endpoints import *
from .endpoints.cache import EndpointCache
from .utils import default_headers

if six.PY3:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin

_default_timeout = 5
_session = requests.Session()

class MHClientHTTPError(Exception):
    pass

def handle_http_exceptions(callbacks={}):
    def wrapper(f):
        def newfunc(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except requests.HTTPError as e:
                resp = e.response
                req = resp.request
                if resp.status_code == 404:
                    raise MHClientHTTPError(
                        "Endpoint not found at %s. " % req.url,
                        "Perhaps it is not available on this node?")
                elif resp.status_code == 401:
                    raise MHClientHTTPError("Access denied: %s" % e)
                elif resp.status_code in callbacks:
                    callbacks[resp.status_code](e)
                else:
                    raise
        return newfunc
    return wrapper

class MHClient(object):

    def __init__(self, base_url, user=None, passwd=None, timeout=None, cache_enabled=True):
        self.base_url = base_url
        self.user = user
        self.passwd = passwd
        self.timeout = timeout or _default_timeout
        self.default_headers = default_headers(self.user and self.passwd)
        self.cache_enabled = cache_enabled
        self.cache = EndpointCache()

    @handle_http_exceptions()
    def endpoints(self):
        """
        Retrieve the list of REST endpoint descriptions
        :return: list of dicts containing details on each endpoint available
        """
        return InfoEndpoint.endpoints(self)

    @handle_http_exceptions()
    def me(self):
        """
        Retrieve information about the current client user
        :return: dict containing info about the user, user's role(s), organization, etc
        """
        return InfoEndpoint.me(self)

    @handle_http_exceptions()
    def user_actions(self, **kwargs):
        actions = UserTrackingEndpoint.user_actions(self, **kwargs)
        return [UserAction(x, self) for x in actions]

    @handle_http_exceptions()
    def workflows(self, **kwargs):
        wfs = WorkflowEndpoint.instances(self, **kwargs)
        return [Workflow(x, self) for x in wfs]

    @handle_http_exceptions()
    def workflow(self, instance_id):
        wf = WorkflowEndpoint.instance(self, instance_id)
        return Workflow(wf, self)

    @handle_http_exceptions()
    def episodes(self, **kwargs):
        eps = EpisodeEndpoint.episodes(self, **kwargs)
        return [Episode(x, self) for x in eps]

    @handle_http_exceptions()
    def episode(self, episode_id):
        ep = EpisodeEndpoint.episode(self, episode_id)
        return Episode(ep, self)

    @handle_http_exceptions()
    def search_episodes(self, **kwargs):
        eps = SearchEndpoint.episodes(self, **kwargs)
        return [SearchEpisode(x, self) for x in eps]

    @handle_http_exceptions()
    def search_episode(self, episode_id):
        ep = SearchEndpoint.episode(self, episode_id)
        return SearchEpisode(ep, self)

    @handle_http_exceptions()
    def agents(self):
        agents_ = CaptureEndpoint.agents(self)
        return [CaptureAgent(x, self) for x in agents_]

    @handle_http_exceptions()
    def agent(self, agent_name):
        agent_ = CaptureEndpoint.agent(self, agent_name)
        return CaptureAgent(agent_, self)

    @handle_http_exceptions()
    def hosts(self):
        hosts_ = ServicesEndpoint.hosts(self)
        return [ServiceHost(x, self) for x in hosts_]

    @handle_http_exceptions()
    def job(self, job_id):
        job_ = ServicesEndpoint.job(self, job_id)
        return ServiceJob(job_, self)

    @handle_http_exceptions()
    def statistics(self):
        statistics_ = ServicesEndpoint.statistics(self)
        return ServiceStatistics(statistics_, self)

    def _http_auth(self):
        if self.user and self.passwd:
            return HTTPDigestAuth(self.user, self.passwd)

    def get(self, path, params=None, extra_headers=None):
        headers = self.default_headers.copy()

        if extra_headers is not None:
            headers.update(extra_headers)

        url = urljoin(self.base_url, path)

        resp = _session.get(url,
                            params=params,
                            headers=headers,
                            auth=self._http_auth(),
                            timeout=self.timeout
                            )
        resp.raise_for_status()
        return resp.json()

    def post(self, path, data=None, extra_headers=None):
        headers = self.default_headers.copy()

        if extra_headers is not None:
            headers.update(extra_headers)

        url = urljoin(self.base_url, path)

        resp = _session.post(url,
                             data=data,
                             headers=headers,
                             auth=self._http_auth(),
                             timeout=self.timeout
                             )
        resp.raise_for_status()

        return resp

    def clear_cache(self):
        self.cache.clear()
