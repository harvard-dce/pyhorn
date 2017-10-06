import sys
import six

if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest

if six.PY3:
    from urllib.parse import urlparse, parse_qs
else:
    from urlparse import urlparse, parse_qs

from pyhorn import MHClient, MHClientHTTPError
from httmock import all_requests, HTTMock

class TestClient(unittest.TestCase):

    def test_init(self):
        c = MHClient('http://matterhorn.example.edu', 'user', 'passwd')
        self.assertEqual(c.base_url, 'http://matterhorn.example.edu')
        self.assertEqual(c.user, 'user')
        self.assertEqual(c.passwd, 'passwd')

    def test_init_no_auth(self):
        c = MHClient('http://matterhorn.example.edu')
        self.assertIsNone(c._http_auth())

    def test_get(self):
        @all_requests
        def resp_content(url, request):
            return {'status_code': 200,
                    'content': {
                        'req_url': request.url,
                        'req_headers': dict(request.headers.items())
                    },
                    'headers': {'content-type': 'application/json'} }

        c = MHClient('http://matterhorn.example.edu', 'user', 'passwd')
        with HTTMock(resp_content):
            data = c.get('/foo', params={'bar': 'baz'})
            self.assertTrue(data['req_headers']['User-Agent'].startswith('pyhorn'))
            url_parts = urlparse(data['req_url'])
            url_params = parse_qs(url_parts.query)
            self.assertEqual(url_parts.path, '/foo')
            self.assertEqual(url_params['bar'], ['baz'])

    def test_post(self):
        @all_requests
        def resp_content(url, request):
            return {'status_code': 200,
                    'content': {
                        'req_url': request.url,
                        'req_body': request.body,
                        'req_method': request.method
                    }}
        c = MHClient('http://matterhorn.example.edu', 'user', 'passwd')
        with HTTMock(resp_content):
            resp = c.post('/bar/baz', data={'foo': 1, 'fud': False})

        resp_data = resp.json()
        self.assertEqual(resp_data['req_url'], 'http://matterhorn.example.edu/bar/baz')
        self.assertEqual(resp_data['req_method'], 'POST')
        self.assertTrue('fud=False' in resp_data['req_body'])
        self.assertTrue('foo=1' in resp_data['req_body'])

    def test_404_handling(self):
        @all_requests
        def resp_404(url, request):
            return {'status_code': 404}
        c = MHClient('http://matterhorn.example.edu', 'user', 'passwd')
        with HTTMock(resp_404):
            self.assertRaises(MHClientHTTPError, c.me)

    def test_401_handling(self):
        @all_requests
        def resp_401(url, request):
            return {'status_code': 401}
        c = MHClient('http://matterhorn.example.edu', 'user', 'passwd')
        with HTTMock(resp_401):
            self.assertRaises(MHClientHTTPError, c.me)
