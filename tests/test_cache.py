import six
import datetime
import mock
import pytest
from freezegun import freeze_time
from pyhorn.endpoints import cache, base

if six.PY3:
    import pickle
else:
    import cPickle as pickle

@pytest.mark.parametrize("args,kwargs,expected", [
    ([1], {'foo': 1}, ([1], frozenset(set([('foo', 1)])))),
    (["id"], {}, (["id"], frozenset({}))),
    (["12345", True], {"foo": 1, "bar": 2}, (["12345", True], frozenset(set([('foo', 1),('bar',2)]))))
])
def test_key_generator(args, kwargs, expected):
    assert cache._generate_cache_key(args, kwargs) == expected

@pytest.fixture
def c():
    return cache.EndpointCache()

@pytest.fixture
def mock_client():
    return mock.Mock(cache_enabled=True, cache=cache.EndpointCache())

@cache.cached(10, 100)
def foo(cls, client, foo_id):
    return (cls, foo_id)

def test_cache_disabled(mock_client):
    mock_client.cache_enabled = False
    with mock.patch('pyhorn.endpoints.cache._generate_cache_key') as mock_key_gen:
        res = foo('Foo', mock_client, "id")
        # not sure how else to test except to check that wrapper never made it this far
        assert mock_key_gen.call_count == 0
    assert res == ('Foo', 'id')

def test_cache_enabled(mock_client):
    res = foo(object, mock_client, 'id')
    assert 'object.foo' in mock_client.cache._caches

def test_cache_set(c):
        c.set('foo', 'bar', 1)
        assert len(c._caches['foo']) == 1
        assert 'bar' in c._caches['foo']
        assert pickle.loads(c._caches['foo']['bar']) == 1

        c.set('foo', 'bar', 2)
        assert len(c._caches['foo']) == 1
        assert 'bar' in c._caches['foo']
        assert pickle.loads(c._caches['foo']['bar']) == 2

def test_cache_set_ttl(c):
    with freeze_time('2016-04-18 00:00:00'):
        c.set('foo', 'bar', 1)
        assert 'bar' in c._expire_info['foo']
        assert c._expire_info['foo']['bar'] == 1460937600.0 + cache.DEFAULT_TTL

        c.set('foo', 'bar', 2, ttl=1000)
        assert pickle.loads(c._caches['foo']['bar']) == 2
        assert 'bar' in c._expire_info['foo']
        assert c._expire_info['foo']['bar'] == 1460937600.0 + 1000

def test_cache_set_max_entries(c):
    with mock.patch.object(c, '_cull') as mock_cull:
        c.set('foo', 'bar', 1)
        c.set('foo', 'baz', 2)
        c.set('foo', 'bear', 3)
        assert mock_cull.call_count == 0
        c.set('foo', 'bez', 4, max_entries=3)
        assert mock_cull.call_count == 1

def test_cache_clear(c):
    c.set('foo', 'bar', 1)
    c.set('foo', 'baz', 2)
    c.set('fob', 'bear', 1)
    c.set('fob', 'beez', 2)
    c.set('bar', 'baz', 1)
    assert len(c._caches['foo']) == 2
    assert len(c._caches['fob']) == 2
    assert len(c._caches['bar']) == 1
    c.clear('foo')
    assert len(c._caches['foo']) == 0
    assert len(c._caches['fob']) == 2
    c.clear()
    assert len(c._caches['fob']) == 0
    assert len(c._caches['bar']) == 0

def test_cache_get(c):
    c.set('foo', 'bar', 100)
    assert c.get('foo', 'bar') == 100

def test_cache_get_expired(c):
    with freeze_time('2010-12-09 00:00:00') as ft:
        c.set('foo', 'bar', 300, ttl=10)
        assert c.get('foo', 'bar') == 300

        ft.tick(datetime.timedelta(seconds=9))
        assert c.get('foo', 'bar') == 300

        ft.tick(datetime.timedelta(seconds=1))
        assert c.get('foo', 'bar') is None

def test_cull(c):
    for i in range(100):
        c.set('foo', str(i), i)
    assert len(c._caches['foo']) == 100
    c._cull('foo')
    assert len(c._caches['foo']) == 66
