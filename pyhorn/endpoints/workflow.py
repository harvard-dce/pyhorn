
import six
from .base import Endpoint, EndpointObj
from .cache import cached

if six.PY3:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin

__all__ = ['WorkflowEndpoint', 'Workflow', 'WorkflowOperation']

class WorkflowEndpoint(Endpoint):

    _kwarg_map = {
        'instances': {
            'compact': None,
             'contributor': None,
             'count': 0,
             'creator': None,
             'fromdate': None,
             'language': None,
             'license': None,
             'mp': None,
             'op': None,
             'q': None,
             'seriesId': None,
             'seriesTitle': None,
             'sort': None,
             'startPage': 0,
             'state': None,
             'subject': None,
             'title': None,
             'todate': None,
             'workflowdefinition': None
        }
    }

    @classmethod
    def instances(cls, client, **kwargs):
        params = cls.map_kwargs_to_params('instances', kwargs)
        resp_data = client.get('workflow/instances.json', params)
        if 'workflow' not in resp_data['workflows']:
            return []
        wfs = resp_data['workflows']['workflow']
        if isinstance(wfs, dict):
            return [wfs]
        return wfs

    @classmethod
    @cached(ttl=60, max_entries=1000)
    def instance(cls, client, instance_id):
        instance_data = client.get('workflow/instance/%s.json' % str(instance_id))
        return instance_data['workflow']


class WorkflowOperation(EndpointObj):

    def __repr__(self):
        return "Operation %s" % self.id

    @property
    def duration(self):
        """
        :return: elapsed time from operation start to completion in milliseconds
        """
        if 'completed' not in self._raw or 'started' not in self._raw:
            return -1
        return self._raw['completed'] - self._raw['started']

    @property
    def job(self):
        from .services import ServicesEndpoint, ServiceJob
        if 'job' not in self._raw:
            return None
        return self._ref_property('job', endpoint_method=ServicesEndpoint.job,
                                  endpoint_params={'job_id': self._raw['job']},
                                  class_=ServiceJob, single=True)

class Workflow(EndpointObj):

    def __repr__(self):
        return "Workflow %s" % self.id

    @property
    def url(self):
        return urljoin(self.client.base_url,
                        "workflow/instance/%d.json" % int(self.id))

    def operation_count(self):
        return len(self.operations)

    @property
    def operations(self):
        return self._ref_property('operations', path_key='operations.operation',
                                       class_=WorkflowOperation)

    def duration(self, inc_op_ids=None, ex_op_ids=None,
                  inc_op_states=None, ex_op_states=None):
        """
        Include/exclude lists are case-sensitive.
        ids should be lowercase strings; states uppercase.
        :param inc_op_ids:
        :param ex_op_ids:
        :param inc_op_states:
        :param ex_op_states:
        :return:
        """
        ops = self.operations

        if inc_op_ids is not None:
            ops = filter(lambda x: x.id in inc_op_ids, ops)
        if inc_op_states is not None:
            ops = filter(lambda x: x.state in inc_op_states, ops)
        if ex_op_ids is not None:
            ops = filter(lambda x: x.id not in ex_op_ids, ops)
        if ex_op_states is not None:
            ops = filter(lambda x: x.state not in ex_op_states, ops)

        return sum([op.duration for op in ops])

    @property
    def mediapackage(self):
        from pyhorn.endpoints import Mediapackage
        return self._ref_property('mediapackage', path_key='mediapackage',
                                   class_=Mediapackage, single=True)

    @property
    def episode(self):
        from pyhorn.endpoints import EpisodeEndpoint, Episode
        return self._ref_property('episode', endpoint_method=EpisodeEndpoint.episode,
                                  endpoint_params={'episode_id': self._raw['mediapackage']['id']},
                                  class_=Episode, single=True)
    @property
    def job(self):
        from .services import ServicesEndpoint, ServiceJob
        return self._ref_property('job', endpoint_method=ServicesEndpoint.job,
                                  endpoint_params={'job_id': self._raw['id']},
                                  class_=ServiceJob, single=True)
