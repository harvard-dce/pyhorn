__author__ = 'jluker'

from base import Endpoint, EndpointObj

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
    def instance(cls, client, instance_id):
        instance_data = client.get('workflow/instance/%s.json' % str(instance_id))
        return instance_data['workflow']


class WorkflowOperation(EndpointObj):
    pass


class Workflow(EndpointObj):

    @property
    def operations(self):
        return self._ref_property('operations', path_key='operations.operation',
                                       class_=WorkflowOperation)



