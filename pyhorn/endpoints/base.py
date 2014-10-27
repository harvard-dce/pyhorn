__author__ = 'jluker'

class Endpoint(object):

    @classmethod
    def map_kwargs_to_params(cls, method, kwargs):
        """
        TODO: look into making this a decorator when the dust settles
        :param method: name of method to look up in the class's _kwarg_map
        :param kwargs: dict of values to map to the endpoint's query string params
        :return: dict of query string param values
        """
        kwarg_map = cls._kwarg_map[method]
        params = {}
        for param, default in kwarg_map.iteritems():
            if kwargs.has_key(param):
                # don't send empty params
                if kwargs[param] is None:
                    continue
                val = kwargs[param]
            elif default is not None:
                val = default
            else:
                continue
            if isinstance(val, bool):
                # stringify booleans
                val = str(val).lower()
            params[param] = val
        return params


class EndpointObj(object):

    def __init__(self, raw_data, client):
        self._raw = dict((k.replace('-','_'), v) for k,v in raw_data.iteritems())
        self._property_stash = {}
        self.client = client

    def _get_raw(self, path_key):
        path_parts = path_key.split('.')
        data = self._raw[path_parts.pop(0)]
        for key in path_parts:
            if key not in data:
                return None
            data = data[key]
        return data

    def _ref_property(self, name, endpoint_method=None, endpoint_params=None,
                          path_key=None, class_=None, single=False):
        if name in self._property_stash:
            return self._property_stash[name]

        if endpoint_method is not None:
            items = endpoint_method(self.client, **endpoint_params)
        elif path_key is not None:
            items = self._get_raw(path_key)

        if items is None:
            items = []
        elif isinstance(items, dict):
            items = [items]

        if class_ is not None:
            items = [class_(x, self.client) for x in items]

        if single:
            items = len(items) > 0 and items[0] or None

        self._property_stash[name] = items

        return items

    def __getattr__(self, attribute):

        if attribute in self._raw:
            return self._raw[attribute]

        # if attribute in self._ref_map:
        #     (method, source_attr, param_name) = self._ref_map[attribute]
        #     param_map = { param_name: getattr(self, source_attr) }
        #     referent = method(self.client, **param_map)
        #     setattr(self, attribute, referent)
        #     return referent

        print "got here with attribute: %s" % attribute
        raise AttributeError("response data for %r has no key %r" %
                              (self.__class__, attribute))


