import os
from httmock import all_requests, urlmatch

base_path = os.path.join(os.path.dirname(__file__), 'fixtures')

def json_fixture(path_match=None, response_data={}, status_code=200):

    def fixture_response(url, req):
        return {'status_code': status_code,
                 'content': response_data,
                 'headers': {'content-type': 'application/json'}}
    if path_match is None:
        return all_requests(fixture_response)
    return urlmatch(path=path_match)(fixture_response)

