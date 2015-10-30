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

