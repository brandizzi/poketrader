from django.test import TestCase, RequestFactory

from .views import index, reset, remove


class ViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.session = {}

    def _get_request(self, path, **data):
        request = self.factory.post(path, data)

        request.session = self.session

        return request


class IndexTest(ViewTestCase):

    def test_add_to_session(self):
        request = self._get_request(
            '/', pokemon_set='1', pokemon_name='pikachu')

        response = index(request)

        self.assertEqual(response.status_code, 302)

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

    def test_index_multiple(self):
        request = self._get_request(
            '/', pokemon_set='1', pokemon_name='pikachu')
        index(request)

        request = self._get_request(
            '/', pokemon_set='1', pokemon_name='charmander')
        index(request)

        request = self._get_request(
            '/', pokemon_set='1', pokemon_name='bulbasaur')
        index(request)

        list1 = request.session['pokemon_list1']
        self.assertEqual(len(list1), 3)


class ResetTest(ViewTestCase):

    def test_reset_session(self):
        request = self._get_request(
            '/', pokemon_set='1', pokemon_name='pikachu')

        response = index(request)

        list1 = request.session['pokemon_list1']
        self.assertEqual(len(list1), 1)

        request = self._get_request('/reset', pokemon_set='1')

        response = reset(request)

        self.assertEqual(response.status_code, 302)

        list1 = request.session['pokemon_list1']
        self.assertEqual(len(list1), 0)
