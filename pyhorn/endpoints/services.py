
from base import Endpoint, EndpointObj
from urlparse import urljoin

__all__ = ['ServicesEndpoint', 'ServiceJob', 'ServiceHost']

class ServicesEndpoint(Endpoint):

    _kwarg_map = {}

    @classmethod
    def hosts(cls, client):
        resp_data = client.get('/services/hosts.json')
        if 'host' not in resp_data['hosts']:
            return []
        hosts = resp_data['hosts']['host']
        if isinstance(hosts, dict):
            return [hosts]
        return hosts

    @classmethod
    def job(cls, client, job_id):
        resp_data = client.get('/services/job/%s.json' % str(job_id))
        return resp_data['job']

    @classmethod
    def children(cls, client, job_id):
        resp_data = client.get('/services/job/%s/children.json' % str(job_id))
        if 'job' not in resp_data['jobs']:
            return []
        children_ = resp_data['jobs']['job']
        if isinstance(children_, dict):
            return [children_]
        return children_

class ServiceHost(EndpointObj):
    pass

class ServiceJob(EndpointObj):

    def __repr__(self):
        return "Job %s" % self.id

    @property
    def url(self):
        return urljoin(self.client.base_url,
                       "services/job/%d.json" % int(self.id))

    def child_count(self):
        return len(self.children)

    @property
    def children(self):
        return self._ref_property('children', endpoint_method=ServicesEndpoint.children,
                                   endpoint_params={'job_id': self._raw['id']},
                                   class_=ServiceJob)

    @property
    def parent(self):
        if self._raw['parentJobId'] == -1:
            return None
        return self._ref_property('parent', endpoint_method=ServicesEndpoint.job,
                                  endpoint_params={'job_id': self._raw['parentJobId']},
                                  class_=ServiceJob, single=True)
