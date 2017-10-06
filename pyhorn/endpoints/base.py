"""
pyhorn.endpoints.base
~~~~~~~~~~~~~~
base classes for endpoint and object wrapper classes
"""

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
        for param, default in kwarg_map.items():
            if param in kwargs:
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
        self._raw = dict((k.replace('-','_'), v) for k,v in raw_data.items())
        self._property_stash = {}
        self.client = client

    @property
    def url(self):
        raise NotImplementedError

    def raw_get(self, path_key, default=None):
        """
        Get any value from the raw data, or None if not found
        :param path_key: path into the raw data structure using dot notation.
                          For example, "foo.bar.baz" would look for
                          self._raw['foo']['bar']['baz']
        :return: whatever is found at the specified path or None
        """
        path_parts = path_key.split('.')
        pointer = self._raw
        for key in path_parts:
            if key not in pointer:
                return default
            pointer = pointer[key]
        return pointer

    def _ref_property(self, name, endpoint_method=None, endpoint_params=None,
                          path_key=None, class_=None, single=False):
        if name in self._property_stash:
            return self._property_stash[name]

        if endpoint_method is not None:
            items = endpoint_method(self.client, **endpoint_params)
        elif path_key is not None:
            items = self.raw_get(path_key)

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

        raise AttributeError("response data for %r has no key %r" %
                              (self.__class__, attribute))

