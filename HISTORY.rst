.. :changelog:

Release History
---------------

0.1.0 (2014-10-23)
++++++++++++++++++

* Birth!

0.1.1 (2014-10-28)
++++++++++++++++++

* copyright tweak

0.1.2 (2014-10-28)
++++++++++++++++++

* blerg. forgot to update history with last version bump.

0.2.0 (2014-11-12)
++++++++++++++++++

* expanded endpoint methods and wrapper objects
* better endpoint class test coverage and fixture/mocking approach

0.3.0 (2015-05-07)
++++++++++++++++++

UserAction.episode now fetches from SearchEndpoint

* new SearchEndpoint for fetching episode data
* new client methods: search_episodes(), search_episode()

0.3.1 (2015-08-04)
++++++++++++++++++

bug fix in client http exception handling

0.4.1 (2015-08-27)
++++++++++++++++++

Additional services endpoint methods

* basic service listing and statistics
* methods for getting count of queued/running jobs
* maintenance on/off

Added request timeouts

Unhandled http exceptions are now re-raised

0.5.0 (2015-10-30)
++++++++++++++++++

* added is_live() method to UserAction
* workflow is now a property Mediapackage objects

0.6.0 (2016-04-14)
++++++++++++++++++

* add new `includeDeleted` param for episode search

0.7.0 (2016-04-14)
++++++++++++++++++

* ripped out the braindead use of requests_cache
* new per-endpoint method caching mechanism

0.8.0 (2016-07-29)
++++++++++++++++++

* allow client creation and usage without user/pass auth
  (note: requests will fail for endpoints that require auth)

0.8.1 (2016-09-20)
++++++++++++++++++

* SearchEpisode endpoint was missing `sort` param

0.9.0 (2018-08-29)
++++++++++++++++++

* Python 3 compatibility!
