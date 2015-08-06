======
pyhorn
======

pyhorn is a python client for accessing the RESTful API of the
`Opencast Matterhorn <http://opencast.org/matterhorn/>`_
video capture system. It provides a client interface, **MHClient**, that exposes methods
for accessing both raw and 'objectified' response data from the various Matterhorn
REST API endpoints.

This software should be considered Alpha, therefore likely to change/break in the
near future.

Install
-------
.. code-block:: bash

    pip install pyhorn

Overview
--------
Data available from the REST endpoints is accessible through methods of the MHClient
object. In many cases the response data is encapsulated in additional classes to make
accessing various attributes of the data possible using object notation. For instance,
data about Matterhorn workflows can be accessed using the ``client.workflows()``
method. The return value will be a list of ``endpoints.workflow.Workflow`` objects.
The ``operations`` attribute of those objects will get you a list of
``endpoints.workflow.WorkflowOperation`` objects. And so forth.

Currently there are only a handfull of endpoints wrapped in this way, and only a
few convenience classes and methods defined for each one. The idea is to continue
adding more as I (or you) need them. Pull requests welcome!

MHClient Method List
--------------------
In the case of methods that accept a set of keyword arguments, the list of expected
kwargs is mapped directly from the Matterhorn endpoint. In other words, if you
want to know what kwargs to use for ``MHClient.workflows()``, check the corresponding
entry in the REST API docs at http://matterhorn.example.edu/docs.html?path=/workflow.

* ``endpoints()`` - /info/components.json
* ``me()`` - /info/me.json
* ``workflows(**kwargs)`` - /workflow/instances.json
* ``workflow(instance_id)`` - /workflow/instance/{id}.json
* ``episodes(**kwargs)`` - /episode/episode.json
* ``episode(episode_id)`` - /episode/episode.json
* ``user_actions(**kwargs)`` - /usertracking/actions.json
* ``agents()`` - /capture-admin/agents.json
* ``agent(agent_name)`` - /capture-admin/agents/{agent_name}.json
* ``hosts()`` - /services/hosts.json
* ``job(job_id)`` - /services/job/{job_id}.json
* ``search_episodes(**kwargs)`` - /search/episode.json
* ``search_episode(episode_id)`` - /search/episode.json

Example Usage
-------------
Create the client interface...

.. code-block:: python

    >>> from pyhorn import MHClient
    >>> client = MHClient('http://matterhorn.example.edu', 'user', 'passwd')

Get a list of available endpoints...

.. code-block:: python

    >>> client.endpoints()
    [{u'description': u'Capture Agent Admin REST Endpoint',
        u'docs': u'http://matterhorn.example.edu80/capture-admin/docs',
        u'path': u'/capture-admin',
        u'type': u'org.opencastproject.capture.admin',
        u'version': u'1.4.4',
        u'wadl': u'http://matterhorn.example.edu80/capture-admin/?_wadl&_type=xml'},
        {u'description': u'EpisodeService REST Endpoint',
        u'docs': u'http://matterhorn.example.edu80/episode/docs',
        u'path': u'/episode',
        u'type': u'org.opencastproject.episode',
        u'version': u'1.4.4',
        u'wadl': u'http://matterhorn.example.edu80/episode/?_wadl&_type=xml'},
    ...
        
Get list of current workflow instances...

.. code-block:: python

    >>> wfs = client.workflows()
    >>> for wf in wfs:
            print wf.id + ": " + wf.state
    1646: STOPPED
    1649: STOPPED
    1651: STOPPED
    1655: STOPPED
    4211: SUCCEEDED
    14479: SUCCEEDED
    14486: SUCCEEDED
    441: STOPPED
    445: STOPPED
    ...

... or just the successful ones...

.. code-block:: python

    >>> wfs = client.workflows(state="SUCCEEDED")

... or the operations for a particular instance...

.. code-block:: python

    >>> wf = client.workflow(instance_id=1646)
    >>> ops = wf.operations
    >>> for op in ops:
        print op.id + ": " + op.state
    apply-acl: SUCCEEDED
    tag: SUCCEEDED
    tag: SUCCEEDED
    inspect: SUCCEEDED
    prepare-av: SUCCEEDED
    prepare-av: SUCCEEDED
    compose: SUCCEEDED
    compose: SUCCEEDED
    ...

Get the list of currently configured capture agents

.. code-block:: python

    >>> cas = client.agents()
    >>> for ca in cas:
        print ca.name + ": " + ca.state
    epiphan001: unknown
    epiphan002: unknown
    ewave001: idle
    ewave002: idle
    ncast001: idle
    ncast002: shutting_down

Endpoint Object Wrappers
------------------------

pyhorn attempts to make the Matterhorn API responses more convenient to work with
by wrapping the json response data in a set of classes that provide easy access
via object attributes and automatic "dereferencing" of associated data.

The following endpoint data classes are defined:

* Workflow
* WorkflowOperation
* ServiceJob
* Episode
* Mediapackage
* MediaTrack
* CaptureAgent
* UserAction
* Search

These are just the initial set because they represent the data I needed to deal
with in the other projects that prompted the creation of pyhorn. It is trivial
to add additional wrapper classes. Pull requests welcome!

**Attribute access**

Endpoint data classes inherit from ``pyhorn.endpoints.base.EndpointObj``. The
json response data is stored in a ``_raw`` attribute and made accessible via
dot-notation by overriding ``__getattr__``. A simple illustration:

.. code-block:: python

    >>> from pyhorn.endpoints.base import EndpointObj
    >>> obj = EndpointObj({"foo": "bar", "baz": [1,2,3]}, client)
    >>> obj.foo
    bar
    >>> obj.baz
    [1, 2, 3]
    >>> obj.abc
    Traceback ...
    ...
    AttributeError: response data for <class 'pyhorn.endpoints.base.EndpointObj'> has no key 'abc'

At this point the dot-notation access only works for top-level values. There is a ``EndpointObj.raw_get`` method
that accepts a ``path_key`` argument if you need to access something deeper in the response
structure.

.. code-block:: python

    >>> obj = EndpointObj({"foo": {"bar": {"baz": 1}}})
    >>> obj.raw_get("foo.bar.baz")
    1

**Dereferencing**

In a handful of cases accessing certain attributes (``@property``, actually)
of an endpoint data wrapper object
will return an instance or instances of a different wrapper class. For example,
``Workflow.operations`` will extract the operation data from the raw json and
return a list of ``WorkflowOperation`` objects that wrap the individual operation
data structures contained in the original response.

This works also for dereferencing data that requires an additional request to the
Matterhorn API. For instance, Accessing the ``WorkflowOperation.job`` property
triggers a request to the ``/services/job/{job_id}.json``, with the response
being wrapped in a ``ServiceJob`` object, cached (of course) and returned.

The current list of these dereferencing relationships is:

* ``Workflow.operations`` -> list of ``WorkflowOperation`` objects
* ``Workflow.job`` -> ``ServiceJob``
* ``Workflow.episode`` -> ``Episode``
* ``Workflow.mediapackage`` -> ``Mediapackage``
* ``WorkflowOperation.job`` -> ``ServiceJob``
* ``ServiceJob.parent`` -> ``ServiceJob``
* ``ServiceJob.children`` -> list of ``ServiceJob`` objects
* ``Episode.mediapackage`` -> ``Mediapackage``
* ``Mediapackage.tracks`` -> list of ``MediaTrack`` objects
* ``UserAction.episode`` -> ``SearchEpisode``

Testing
-------

During development pyhorn tests are executed using `pytest <https://pytest.org/latest/contents.html>`_.

To run the tests from a local git clone:

.. code-block:: bash

    pip install -r tests/requirements.txt

then

.. code-block:: bash

    python setup.py test

License
-------
pyhorn is licensed under the Apache 2.0 license

Copyright
---------
2014 President and Fellows of Harvard College

