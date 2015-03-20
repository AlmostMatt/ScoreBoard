from django.test import TestCase, Client
from tsw.models import *
from tsw.views import *

from django.core.urlresolvers import reverse

from django.utils import timezone
import json

class SanityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.u1 = User.objects.create(name='Some user', create_date=timezone.now(), secret_code=randint(0, 1000000000))

    def test_server_info(self):
        params = {'domain': 'test.com'}
        response = self.client.get(reverse('tsw.views.server_info'), params)
        assert response.status_code == 200, 'Status code %s' % response.status_code
        data = json.loads(response.content)
        assert data['swf_url']
        assert data['base_url']

    def test_new_user(self):
        params = {'name': ''}
        response = self.client.post(reverse('tsw.views.new_user'), params, HTTP_REFERER='http://test_new_user.com/asdf/')
        assert response.status_code == 200, 'Status code %s' % response.status_code
        data = json.loads(response.content)
        assert data['name'][:4] == 'Anon'
        assert data['user_id']
        assert data['secret_code']
        assert data['create_date']

    def test_scores(self):
        params = {'user_id': self.u1.id, 'secret_code': self.u1.secret_code, 'score': 37, 'replay': '', 'level': 3}
        response = self.client.post(reverse('tsw.scores.save_score'), params)
        assert response.status_code == 200, 'Status code %s' % response.status_code
        data = json.loads(response.content)
        assert data['user_id']
        assert data['score']

        params = {'user_id': self.u1.pk, 'secret_code': self.u1.secret_code, 'level': 3}
        response = self.client.get(reverse('tsw.scores.get_scores'), params)
        assert response.status_code == 200, 'Status code %s' % response.status_code
        data = json.loads(response.content)
        assert data['num_scores'] == 1
        assert data['top_scores'][0]['user_id'] == self.u1.pk

# future tests: date filters, sorting, get scores cases, w/e
# also test unicode and long fields/missing malformed fields

# verify side effects (metrics, objects)

