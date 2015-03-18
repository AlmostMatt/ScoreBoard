from django.test import TestCase, Client
from tsw.models import *
from tsw.views import *

from django.core.urlresolvers import reverse

import json

class SanityTest(TestCase):
    def setup(self):
        self.client = Client()

    def test_server_info(self):
        params = {'domain': 'test.com'}
        response = self.client.get(reverse('tsw.views.server_info'), params)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['swf_url']
        assert data['base_url']

    def test_new_user(self):
        params = {'name': ''}
        response = self.client.get(reverse('tsw.views.new_user'), params)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['name'][:4] == 'Anon'
        assert data['user_id']
        assert data['secret_code']
        assert data['create_date']

# future tests: date filters, sorting, get scores cases, w/e
# also test unicode and long fields/missing malformed fields

# verify side effects (metrics, objects)

