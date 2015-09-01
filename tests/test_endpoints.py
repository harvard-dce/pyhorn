
import os
import requests_cache

os.environ['TESTING'] = 'True'

import sys
if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest

import requests
from pyhorn import MHClient
from pyhorn.endpoints import *
from pyhorn.endpoints.base import *
from httmock import urlmatch, HTTMock
from mock import patch, Mock
from fixtures import json_fixture

class EndpointTestCase(unittest.TestCase):

    def setUp(self):
        self.c = MHClient('http://matterhorn.example.edu', 'user', 'pass')

class TestBaseEndpoint(EndpointTestCase):
    """
    Test the underlying endpoing class methods
    """
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

        WorkflowEndpoint._kwarg_map =  save_kwarg_map

    def test_endpoint_obj(self):
        obj = EndpointObj({
            "foo": 1,
            "bar": "baz",
            "blah": {
                "blerg": 3,
                "blymie": {
                    "ahoy": "hello!"
                }
            }
        }, self.c)

        self.assertEqual(obj.foo, 1)
        self.assertEqual(obj.bar, "baz")
        self.assertRaises(AttributeError, getattr, obj, "abc")

        self.assertEqual(obj.raw_get("foo"), 1)
        self.assertEqual(obj.raw_get("foot"), None)
        self.assertEqual(obj.raw_get("foot", "abcd"), "abcd")
        self.assertEqual(obj.raw_get("blah.blerg"), 3)
        self.assertEqual(obj.raw_get("blah.blymie"), {"ahoy": "hello!"})
        self.assertEqual(obj.raw_get("blah.blymie.ahoy"), "hello!")

        self.assertRaises(NotImplementedError, getattr, obj, "url")

    def test_ref_property_path(self):

        class Foo(EndpointObj):
            pass

        obj = EndpointObj({
            "a": {
                "b": {
                    "hola": "ciao!"
                },
                "c": [
                    {"bar": 1},
                    {"baz": 2}
                ]
            }
        }, self.c)

        # should return list of Foo obj
        ref_obj = obj._ref_property('foo', path_key="a.b", class_=Foo)
        self.assertTrue(isinstance(ref_obj, list))
        self.assertTrue(isinstance(ref_obj[0], Foo))
        self.assertEqual(ref_obj[0].hola, "ciao!")
        self.assertTrue(isinstance(obj._property_stash['foo'], list))

        # should get the stashed value if called again
        obj._property_stash['foo'] = 1
        ref_obj = obj._ref_property('foo', path_key="a.b", class_=Foo)
        self.assertEqual(ref_obj, 1)
        del obj._property_stash['foo']

        # ... or one obj if single=True
        ref_obj = obj._ref_property('foo', path_key="a.b", class_=Foo, single=True)
        self.assertTrue(isinstance(ref_obj, Foo))
        self.assertEqual(ref_obj.hola, "ciao!")

        ref_obj = obj._ref_property('boo', path_key="a.c", class_=Foo)
        self.assertTrue(isinstance(ref_obj, list))
        del obj._property_stash['boo']

        ref_obj = obj._ref_property('boo', path_key="a.c", class_=Foo, single=True)
        self.assertTrue(isinstance(ref_obj, Foo))
        self.assertEqual(ref_obj.bar, 1)

    def test_ref_property_endpoint_method(self):

        class Foo(EndpointObj):
            pass

        obj = EndpointObj({
            "foo_id": 12345
        }, self.c)

        def fake_endpoint_method(client, **params):
            return [params]

        ref_obj = obj._ref_property('foo', endpoint_method=fake_endpoint_method,
                                    endpoint_params={'id': obj.foo_id}, class_=Foo)
        self.assertTrue(isinstance(ref_obj, list))
        del obj._property_stash['foo']

        ref_obj = obj._ref_property('foo', endpoint_method=fake_endpoint_method,
                                    endpoint_params={'id': obj.foo_id}, class_=Foo, single=True)
        self.assertTrue(isinstance(ref_obj, Foo))
        self.assertEqual(ref_obj.id, 12345)

class TestInfo(EndpointTestCase):

    def test_components(self):
        comp_data = json_fixture(response_data={
            "ui": [],
            "rest": [
                { "path": "/ingest" },
                { "path": "/mediapackage" },
                { "path": "/workflow" }
            ]
        })

        with HTTMock(comp_data):
            data = InfoEndpoint.components(self.c)
        self.assertTrue(isinstance(data, dict))
        self.assertTrue(isinstance(data['rest'], list))
        self.assertEqual([x['path'] for x in data['rest']], ['/ingest', '/mediapackage', '/workflow'])

class TestWorkflows(EndpointTestCase):

    def test_instances(self):
        wfs_data = json_fixture(response_data={
            "workflows": {
                "workflow": [
                    { "id": "1" },
                    { "id": "2" },
                ]
            }
        })
        with HTTMock(wfs_data):
            wfs = WorkflowEndpoint.instances(self.c)
        self.assertTrue(isinstance(wfs, list))
        self.assertTrue(isinstance(wfs[0], dict))

    def test_instance(self):
        wf_data = json_fixture(response_data={
            "workflow": { "id": "123456" }
        })
        with HTTMock(wf_data):
            wf = WorkflowEndpoint.instance(self.c, 123456)
        self.assertTrue(isinstance(wf, dict))

    def test_workflow_class(self):
        wf = Workflow({
            "state": "RUNNING",
            "id": 123456,
            "operations": {
                "operation": [
                {"id": "foo"},
                {"id": "bar"}
                ]
            },
            "mediapackage": {
                "id": "abcd-1234"
            }
        }, self.c)

        self.assertTrue(wf.url.startswith(self.c.base_url))
        self.assertTrue(wf.url.endswith("123456.json"))
        self.assertEqual(wf.operation_count(), 2)
        self.assertEqual(str(wf), "Workflow 123456")
        self.assertTrue(isinstance(wf.operations[0], WorkflowOperation))
        self.assertEqual([x.id for x in wf.operations], ["foo", "bar"])
        self.assertTrue(isinstance(wf.mediapackage, Mediapackage))
        self.assertEqual(wf.mediapackage.id, "abcd-1234")

    def test_workflow_episode(self):
        """
        Test that the workflow correctly fetches its associated episode
        """
        ep_data = json_fixture(r'/episode/', {
            "search-results": {
                "result": [
                    { "id": "abcd-1234" },
                ]
            }
        })

        wf = Workflow({
            "mediapackage": {
                "id": "abcd-1234",
            }
        }, self.c)

        with HTTMock(ep_data):
            episode = wf.episode
        self.assertEqual(episode.id, "abcd-1234")

    def test_workflow_job(self):
        """
        Test that the workflow correctly fetches its associated job
        """
        job_data = json_fixture(r'/services/job/', {
            "job": {
                "id": "99999"
            }
        })

        wf = Workflow({
            "id": "99999"
        }, self.c)

        with HTTMock(job_data):
            job = wf.job
        self.assertEqual(job.id, "99999")

    def test_workflow_ops(self):
        wf = Workflow({
            "operations": {
                "operation": [
                {"id": "bar", "started": 1000, "completed": 1050,
                 "state": "foo" },
                {"id": "baz", "started": 2000, "completed": 2100,
                 "state": "foo" },
                {"id": "blah", "started": 3000, "completed": 3200,
                 "state": "fuu" }
                ]
            }
        }, self.c)
        ops = wf.operations
        self.assertEqual(ops[0].id, "bar")
        self.assertEqual(ops[0].duration, 50)
        self.assertEqual(ops[1].duration, 100)
        self.assertEqual(wf.duration(), 350)
        self.assertEqual(wf.duration(inc_op_ids=("bar",)), 50)
        self.assertEqual(wf.duration(inc_op_ids=("bar", "baz")), 150)
        self.assertEqual(wf.duration(ex_op_ids=("bar",)), 300)
        self.assertEqual(wf.duration(ex_op_ids=("bar","blah")), 100)
        self.assertEqual(wf.duration(inc_op_states=("foo",)), 150)
        self.assertEqual(wf.duration(ex_op_states=("foo",)), 200)
        self.assertEqual(wf.duration(inc_op_states=("foo",), ex_op_ids=("bar",)), 100)

    def test_workflow_op_job(self):
        """
        Test that the workflow op correctly fetches its associated job
        """
        job_data = json_fixture(r'/services/job/', {
            "job": {
                "id": "34567"
            }
        })

        op = WorkflowOperation({
            "job": "34567"
        }, self.c)

        with HTTMock(job_data):
            job = op.job
        self.assertEqual(job.id, "34567")

class TestUserTracking(EndpointTestCase):

    def test_actions(self):
        ua_data = json_fixture(response_data={
            "actions": {
                "action": [
                    {"id": 1},
                    {"id": 2}
                ]
            }
        })
        with HTTMock(ua_data):
            actions = UserTrackingEndpoint.user_actions(self.c)
        self.assertTrue(isinstance(actions, list))
        self.assertTrue(isinstance(actions[0], dict))

    def test_action_episode(self):

        ep_data = json_fixture(r'/search/', {
            "search-results": {
                "result": [
                    { "id": "abcd-1234" },
                    ]
            }
        })

        ua = UserAction({
            "mediapackageId": "abcd=1234"
        }, self.c)

        with HTTMock(ep_data):
            episode = ua.episode
        self.assertEqual(episode.id, "abcd-1234")

class TestEpisodes(EndpointTestCase):

    def test_episodes(self):
        ep_data = json_fixture(response_data={
            "search-results": {
                "result": [
                    { "id": "abcd-1234" },
                    { "id": "efgh-1234" }
                ]
            }
        })
        with HTTMock(ep_data):
            episodes = EpisodeEndpoint.episodes(self.c)
        self.assertEqual(len(episodes), 2)

        # both the plural and singular epidsode methods use the same endpoint,
        # the singular just sends back result[0]
        with HTTMock(ep_data):
            episode = EpisodeEndpoint.episode(self.c, 'abcd-1234')
        self.assertTrue(isinstance(episode, dict))

    def test_episode_class(self):
        ep = Episode({
            "id": "abcd-1234"
        }, self.c)

        self.assertTrue(ep.url.startswith(self.c.base_url))
        self.assertTrue(ep.url.endswith("?id=abcd-1234"))
        self.assertEqual(str(ep), "Episode abcd-1234")

    def test_episode_mediapackage(self):

        ep = Episode({
            "mediapackage": {
                "id": "efgh-1234",
                "media": {
                    "track": [
                        { "duration": 5 },
                        { "duration": 10 }
                    ]
                }
            }
        }, self.c)

        mp = ep.mediapackage
        self.assertTrue(isinstance(mp, Mediapackage))
        self.assertEqual(mp.id, "efgh-1234")
        self.assertEqual(str(mp), "Mediapackage efgh-1234")

        tracks = mp.tracks
        self.assertTrue(isinstance(tracks[0], MediaTrack))
        self.assertEqual(tracks[0].duration, 5)

    def test_episode_mp_workflow(self):

        wfs_data = json_fixture(response_data={
            "workflows": {
                "workflow": [
                    { "id": "123456" },
                ]
            }
        })
        mp = Mediapackage({"id": "efgh-1234"}, self.c)

        with HTTMock(wfs_data):
            mp_wf = mp.workflow

        self.assertEqual(mp_wf.id, '123456')

class TestCaptureAgents(EndpointTestCase):

    def test_agents(self):
        ag_data = json_fixture(response_data={
            "agents": {
                "agent": [
                    { "name": "ncast01" },
                    { "name": "ewave01" }
                ]
            }
        })

        with HTTMock(ag_data):
            agents = CaptureEndpoint.agents(self.c)
        self.assertTrue(isinstance(agents, list))

        # check that return is still a list even if only one result
        ag_data = json_fixture(response_data={
            "agents": {
                "agent": { "name": "ewave01" }
            }
        })

        with HTTMock(ag_data):
            agents = CaptureEndpoint.agents(self.c)
        self.assertTrue(isinstance(agents, list))

    def test_agent(self):
        ag_data = json_fixture(response_data={
            "agent-state-update": {
                "name": "epiphan01"
            }
        })

        with HTTMock(ag_data):
            agent = CaptureEndpoint.agent(self.c, "epiphan01")
        self.assertTrue(isinstance(agent, dict))
        self.assertEqual(agent['name'], "epiphan01")

    def test_agent_capabilities(self):
        ca = CaptureAgent({
            "name": "epiphan01",
            "capabilities": {
                "item": [
                    {"key": "foo", "value": 1},
                    {"key": "bar", "value": 2}
                ]
            }
        }, self.c)

        caps = ca.capabilities
        self.assertEqual(caps['foo'], 1)


class TestServices(EndpointTestCase):

    def test_statistics(self):

        stat_data = json_fixture(response_data={
            "statistics": {
                "service": [
                    { "queued": "0" },
                    { "queued": "1" }
                ]
            }
        })

        with HTTMock(stat_data):
            stats = ServicesEndpoint.statistics(self.c)
            self.assertTrue(isinstance(stats, dict))
            stats_obj = self.c.statistics()
            self.assertTrue(isinstance(stats_obj, ServiceStatistics))

    def test_statistics_obj(self):
        stats_obj = ServiceStatistics({
            'statistics': {
                'service': [
                    {
                        'queued': 0,
                        'running': 1,
                        'serviceRegistration': {
                            'type': 'foo',
                            'host': 'http://foo'
                        }
                    },
                    {
                        'queued': 0,
                        'running': 1,
                        'serviceRegistration': {
                            'type': 'fud',
                            'host': 'http://foo'
                        }
                    },
                    {
                        'queued': 1,
                        'running': 2,
                        'serviceRegistration': {
                            'type': 'bar',
                            'host': 'http://bar'
                        }
                    },
                    {
                        'queued': 0,
                        'running': 0,
                        'serviceRegistration': {
                            'type': 'baz',
                            'host': 'http://baz'
                        }
                    },
                    {
                        'queued': 1,
                        'running': 1,
                        'serviceRegistration': {
                            'type': 'baz',
                            'host': 'http://baz'
                        }
                    }
                ]
            }
        }, self.c)
        self.assertTrue(isinstance(stats_obj.services, list))
        self.assertTrue(isinstance(stats_obj.services[0], ServiceStatEntry))
        self.assertTrue(isinstance(stats_obj.services[0].registration, ServiceRegistration))
        self.assertEqual(stats_obj.services[0].type, 'foo')
        self.assertEqual(stats_obj.running_jobs(), 5)
        self.assertEqual(stats_obj.queued_jobs(), 2)
        self.assertEqual(stats_obj.running_jobs(type='bar'), 2)
        self.assertEqual(stats_obj.running_jobs(type='baz'), 1)
        self.assertEqual(stats_obj.running_jobs(type='blergh'), 0)
        self.assertEqual(stats_obj.queued_jobs(type='baz'), 1)
        self.assertEqual(stats_obj.queued_jobs(host='http://bar'), 1)
        self.assertEqual(stats_obj.running_jobs(host='http://foo'), 2)
        self.assertEqual(stats_obj.running_jobs(type='foo', host='http://foo'), 1)

    def test_services(self):

        stat_data = json_fixture(response_data={
            "services": {
                "service": [
                    { "type": "foo" },
                    { "type": "bar" }
                ]
            }
        })

        with HTTMock(stat_data):
            services = ServicesEndpoint.services(self.c)
            self.assertTrue(isinstance(services, list))

    def test_service_host(self):
        services_data = json_fixture(response_data={
            'services': {
                'service': [
                    { "type": "foo", "host": "http://foo.example.edu" },
                    { "type": "bar", "host": "http://foo.example.edu" }
                ]
            }
        })
        host = ServiceHost({ 'base_url': 'http://foo.example.edu' }, self.c)
        with HTTMock(services_data):
            self.assertEqual(len(host.services), 2)
            self.assertEqual(host.services[0].type, "foo")

    @patch.object(requests.Session, 'post', autospec=True)
    @patch.object(requests_cache, 'clear')
    def test_service_host_maintenance(self, mock_clear, mock_post):

        host = ServiceHost({ 'base_url': 'http://foo.example.edu' }, self.c)

        host.set_maintenance(True)
        call_args, call_kwargs = mock_post.call_args
        self.assertEqual(call_args[1], 'http://matterhorn.example.edu/services/maintenance')
        self.assertEqual(call_kwargs['data'], {'host': 'http://foo.example.edu', 'maintenance': True})

        host.set_maintenance(False)
        call_args, call_kwargs = mock_post.call_args
        self.assertEqual(call_kwargs['data'], {'host': 'http://foo.example.edu', 'maintenance': False})
