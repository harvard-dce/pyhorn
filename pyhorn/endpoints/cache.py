import six
import time
from rwlock import RWLock
from functools import wraps
from collections import defaultdict

if six.PY3:
    import pickle
else:
    import cPickle as pickle

DEFAULT_TTL = 300
DEFAULT_MAX_ENTRIES = 3000

def cached(ttl=DEFAULT_TTL, max_entries=DEFAULT_MAX_ENTRIES):
    def wrap(func):
        @wraps(func)
        def wrapped(cls, client, *args, **kwargs):

            if not client.cache_enabled:
                return func(cls, client, *args, **kwargs)

            cache_key = _generate_cache_key(args, kwargs)
            cache_name = cls.__name__ + '.' + func.__name__
            res = client.cache.get(cache_name, cache_key)

            if res is None:
                res = func(cls, client, *args, **kwargs)
                client.cache.set(cache_name, cache_key, res, ttl, max_entries)

            return res

        return wrapped
    return wrap

def _generate_cache_key(args, kwargs):
    return (args, frozenset(kwargs.items()))


class EndpointCache(object):

    def __init__(self):
        self._locks = defaultdict(RWLock)
        self._caches = defaultdict(dict)
        self._expire_info = defaultdict(dict)

    def get(self, method, key, default=None):

        pickled = None
        with self._locks[method].reader_lock:
            if not self._has_expired(method, key):
                pickled = self._caches[method][key]
        if pickled is not None:
            try:
                return pickle.loads(pickled)
            except pickle.PickleError:
                return default

        with self._locks[method].writer_lock:
            try:
                del self._caches[method][key]
                del self._expire_info[method][key]
            except KeyError:
                pass
            return default

    def set(self, method, key, value, ttl=DEFAULT_TTL,
            max_entries=DEFAULT_MAX_ENTRIES):
        with self._locks[method].writer_lock:
            if len(self._caches[method]) >= max_entries:
                self._cull(method)
            self._caches[method][key] = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
            self._expire_info[method][key] = time.time() + ttl

    def _has_expired(self, method, key):
        exp = self._expire_info[method].get(key, -1)
        if exp is None or exp > time.time():
            return False
        return True

    def _cull(self, method):
        # make room by deleting 1/3 of the existing entries
        doomed = [k for (i, k) in enumerate(self._caches[method]) if i % 3 == 0]
        for k in doomed:
            self._delete(method, k)

    def _delete(self, method, key):
        try:
            del self._caches[method][key]
        except KeyError:
            pass
        try:
            del self._expire_info[method][key]
        except KeyError:
            pass

    def clear(self, method=None):

        if method is not None:
            methods = [method]
        else:
            methods = self._caches.keys()

        for method in methods:
            self._caches[method].clear()
            self._expire_info[method].clear()
