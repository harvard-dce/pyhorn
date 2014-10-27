__author__ = 'jluker'

import os
from httmock import all_requests

class JsonFixture:

    def __init__(self, path):
        self.path = path

    def get(self):
        base_path = os.path.dirname(__file__)
        abs_path = os.path.join(base_path, 'endpoints', self.path[1:])
        with open(abs_path, 'r') as f:
            content = f.read()
        return content

@all_requests
def fixture_response(url, request):
    return {'status_code': 200,
             'content': JsonFixture(url.path).get(),
             'headers': {'content-type': 'application/json'} }