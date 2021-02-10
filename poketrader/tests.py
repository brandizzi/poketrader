from django.test import TestCase, RequestFactory

from django.contrib.sessions.middleware import SessionMiddleware

from .views import index


class IndexTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_add_to_session(self):
        request = self._get_request(
            '/', pokemon_set='1', pokemon_name='pikachu')

        response = index(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.session['pokemon_list1'], ['pikachu'])

    def _get_request(self, path, **data):
        request = self.factory.post('/', data)

        middleware = SessionMiddleware()
        middleware.process_request(request)

        request.session.save()

        return request
