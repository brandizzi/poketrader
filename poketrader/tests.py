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

        list1 = request.session['pokemon_list1']
        self.assertEqual(len(list1), 1)

        pokemon = list1[0]
        self.assertEqual(pokemon, {
            'name': 'pikachu',
            'base_experience': 112,
            'picture_url':
                'https://raw.githubusercontent.com/PokeAPI/'
                'sprites/master/sprites/pokemon/25.png'
        })

    def _get_request(self, path, **data):
        request = self.factory.post('/', data)

        middleware = SessionMiddleware()
        middleware.process_request(request)

        request.session.save()

        return request
