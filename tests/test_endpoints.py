__author__ = 'jluker'

import os
os.environ['TESTING'] = 'True'

import sys
if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest

from urlparse import urlparse, parse_qs
from pyhorn import client, MHClient
from pyhorn.endpoints import *
from httmock import all_requests, urlmatch, HTTMock
from fixtures import JsonFixture, fixture_response

class EndpointTestCase(unittest.TestCase):

    def setUp(self):
        self.c = MHClient('http://matterhorn.example.edu', 'user', 'passwd')

class TestBaseEndpoint(EndpointTestCase):

    def test_build_params(self):
        save_kwarg_map = WorkflowEndpoint._kwarg_map.copy()
        WorkflowEndpoint._kwarg_map['instances'] = {
            'param1': None, 'param2': 0, 'param3': "foo", 'param4': False
            }

        def _params_test(kwargs, expected):
            params = WorkflowEndpoint.map_kwargs_to_params('instances', kwargs)
            self.assertEqual(params, expected)

        _params_test({},
                     {'param2': 0, 'param3': "foo", 'param4': 'false'})

        _params_test({'param1': 2},
                     {'param1': 2, 'param2': 0, 'param3': "foo", 'param4': 'false'})

        _params_test({'param1': None},
                     {'param2': 0, 'param3': "foo", 'param4': 'false'})

        _params_test({'param1': 0},
                     {'param1': 0, 'param2': 0, 'param3': "foo", 'param4': 'false'})

        _params_test({'param1': None, 'param2': None, 'param3': None},
                     {'param4': 'false'})

        _params_test({'param1': 0, 'param2': 0, 'param3': 0},
                     {'param1': 0, 'param2': 0, 'param3': 0, 'param4': 'false'})

        _params_test({'param4': True},
                     {'param2': 0, 'param3': 'foo', 'param4': 'true'})

class TestInfo(EndpointTestCase):

    def test_components(self):
        with HTTMock(fixture_response):
            data = InfoEndpoint.components(self.c)
        self.assertTrue(isinstance(data, dict))
        self.assertTrue(isinstance(data['rest'], list))
        self.assertEqual([x['path'] for x in data['rest']], ['/ingest', '/mediapackage', '/workflow'])

class TestWorkflows(EndpointTestCase):

    def test_instances(self):
        with HTTMock(fixture_response):
            wfs = WorkflowEndpoint.instances(self.c)
        self.assertTrue(isinstance(wfs, list))
        self.assertTrue(isinstance(wfs[0], dict))

class TestUserTracking(EndpointTestCase):

    def test_actions(self):
        with HTTMock(fixture_response):
            actions = UserTrackingEndpoint.user_actions(self.c)
        self.assertTrue(isinstance(actions, list))
        self.assertTrue(isinstance(actions[0], dict))

class TestEpisodes(EndpointTestCase):

    def test_episodes(self):
        with HTTMock(fixture_response):
            episodes = EpisodeEndpoint.episodes(self.c)
        self.assertEqual(len(episodes), 3)