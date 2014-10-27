__author__ = 'jluker'

import sys
if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest

import json
from urlparse import urlparse, parse_qs
from pyhorn import client, MHClient
from httmock import all_requests, urlmatch, HTTMock

class TestClient(unittest.TestCase):

    def test_init(self):
        from requests.auth import HTTPDigestAuth
        c = MHClient('http://matterhorn.example.edu', 'user', 'passwd')
        self.assertEqual(c.base_url, 'http://matterhorn.example.edu')
        self.assertEqual(c.user, 'user')
        self.assertEqual(c.passwd, 'passwd')

    def test_get(self):
        @all_requests
        def resp_content(url, request):
            return {'status_code': 200,
                    'content': {
                        'url': request.url,
                        'headers': dict(request.headers.items())
                    },
                    'headers': {'content-type': 'application/json'} }

        c = MHClient('http://matterhorn.example.edu', 'user', 'passwd')
        with HTTMock(resp_content):
            data = c.get('/foo', params={'bar': 'baz'})
            for k, v in client._auth_headers.items():
                self.assertEqual(data['headers'][k], v)
            url_parts = urlparse(data['url'])
            url_params = parse_qs(url_parts.query)
            self.assertEqual(url_parts.path, '/foo')
            self.assertEqual(url_params['bar'], ['baz'])
