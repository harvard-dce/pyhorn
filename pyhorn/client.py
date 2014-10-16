__author__ = 'jluker'

import requests
import requests_cache
from requests.auth import HTTPDigestAuth
from endpoints import *

_auth_headers = {'X-REQUESTED-AUTH': 'Digest',
                 'X-Opencast-Matterhorn-Authorization': 'true'}
_cache_type = 'memory'
requests_cache.install_cache(backend=_cache_type)

_session = requests.Session()

class MHClient(object):

    def __init__(self, base_url, user, passwd):
        self.base_url = base_url
        self.auth = HTTPDigestAuth(user, passwd)

    def components(self):
        return Info.components(self)

    def me(self):
        return Info.me(self)

    def user_actions(self, **kwargs):
        return UserTracking.actions(**kwargs)

