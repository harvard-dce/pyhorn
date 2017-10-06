
import six
from .base import Endpoint, EndpointObj

if six.PY3:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin

__all__ = ['ServicesEndpoint', 'ServiceJob', 'ServiceHost',
           'ServiceStatistics', 'ServiceRegistration', 'ServiceStatEntry']


class ServicesEndpoint(Endpoint):

    _kwarg_map = {
        'services': {
            'serviceType': None,
            'host': None
        }
    }

    @classmethod
    def statistics(cls, client):
        resp_data = client.get('/services/statistics.json')
        return resp_data

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
    def services(cls, client, **kwargs):
        params = cls.map_kwargs_to_params('services', kwargs)
        resp_data = client.get('/services/services.json', params)
        if 'service' not in resp_data['services']:
            return []
        services = resp_data['services']['service']
        if isinstance(services, dict):
            return [services]
        return services

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


class ServiceStatistics(EndpointObj):

    @property
    def services(self):
        return self._ref_property('services', path_key='statistics.service',
                                  class_=ServiceStatEntry)

    def filtered_services(self, host=None, type=None):
        def _filter(s):
            if host is not None and s.registration.host != host:
                return False
            if type is not None and s.registration.type != type:
                return False
            return True
        return filter(_filter, self.services)

    def running_jobs(self, host=None, type=None):
        services = self.filtered_services(host, type)
        return sum(int(x.running) for x in services)

    def queued_jobs(self, host=None, type=None):
        services = self.filtered_services(host, type)
        return sum(int(x.queued) for x in services)


class ServiceStatEntry(EndpointObj):

    @property
    def registration(self):
        return self._ref_property('registration', path_key='serviceRegistration',
                                  class_=ServiceRegistration, single=True)

    @property
    def type(self):
        return self.registration.type

class ServiceRegistration(EndpointObj):
    pass

class ServiceHost(EndpointObj):

    @property
    def services(self):
        return self._ref_property('services', endpoint_method=ServicesEndpoint.services,
                                  endpoint_params={'host': self._raw['base_url']},
                                  class_=ServiceRegistration)

    def set_maintenance(self, state):
        self.client.post('/services/maintenance', data={
                             'host': self.base_url,
                             'maintenance': state
                         })

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
