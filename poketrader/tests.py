from django.test import TestCase, RequestFactory
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib import messages

from .views import index, reset, remove
from .models import Pokemon


class ViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.session = {}

    def _get_post_request(self, path, **data):
        request = self.factory.post(path, data)

        request.session = self.session

        message_middleware = MessageMiddleware()
        message_middleware.process_request(request)

        return request

    def _get_get_request(self, path, **data):
        request = self.factory.get(path, data)

        request.session = self.session

        message_middleware = MessageMiddleware()
        message_middleware.process_request(request)

        return request


class IndexTest(ViewTestCase):

    def test_save_to_database(self):
        pokemons = Pokemon.objects.filter(name='pikachu')

        self.assertEqual(len(pokemons), 0)

        request = self._get_post_request(
            '/', pokemon_set='1', pokemon_name='pikachu')

        response = index(request)

        self.assertEqual(response.status_code, 302)

        pokemons = Pokemon.objects.filter(name='pikachu')

        self.assertEqual(len(pokemons), 1)

        pokemons[0].delete()

    def test_add_to_session(self):
        request = self._get_post_request(
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

    def test_add_to_session_not_found(self):
        request = self._get_post_request(
            '/', pokemon_set='1', pokemon_name='agumon')

        response = index(request)

        self.assertEqual(response.status_code, 302)

        list1 = request.session.get('pokemon_list1', [])
        self.assertEqual(len(list1), 0)

        messages_list = list(messages.get_messages(request))

        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            messages_list[0].message,
            "There is no such Pokémon called \"agumon.\"")

    def test_get_page(self):
        request = self._get_get_request('/')

        response = index(request)

        self.assertEqual(response.status_code, 200)

        list1 = request.session.get('pokemon_list1', [])
        self.assertEqual(len(list1), 0)

    def test_index_multiple(self):
        request = self._get_post_request(
            '/', pokemon_set='1', pokemon_name='pikachu')
        index(request)

        request = self._get_post_request(
            '/', pokemon_set='1', pokemon_name='charmander')
        index(request)

        request = self._get_post_request(
            '/', pokemon_set='1', pokemon_name='bulbasaur')
        index(request)

        list1 = request.session['pokemon_list1']
        self.assertEqual(len(list1), 3)


class ResetTest(ViewTestCase):

    def test_reset_session(self):
        request = self._get_post_request(
            '/', pokemon_set='1', pokemon_name='pikachu')

        response = index(request)

        list1 = request.session['pokemon_list1']
        self.assertEqual(len(list1), 1)

        request = self._get_post_request('/reset', pokemon_set='1')

        response = reset(request)

        self.assertEqual(response.status_code, 302)

        list1 = request.session['pokemon_list1']
        self.assertEqual(len(list1), 0)


class RemoveTest(ViewTestCase):

    def test_remove_pokemon(self):
        request = self._get_post_request(
            '/', pokemon_set='1', pokemon_name='pikachu')
        index(request)

        request = self._get_post_request(
            '/', pokemon_set='1', pokemon_name='charmander')
        index(request)

        request = self._get_post_request(
            '/', pokemon_set='1', pokemon_name='bulbasaur')
        index(request)

        list1 = request.session['pokemon_list1']
        self.assertEqual(len(list1), 3)

        request = self._get_post_request('/remove', pokemon_set='1', index='1')

        response = remove(request)

        self.assertEqual(response.status_code, 302)

        list1 = request.session['pokemon_list1']
        self.assertEqual(len(list1), 2)
        self.assertEqual(list1[0]['name'], 'pikachu')
        self.assertEqual(list1[1]['name'], 'bulbasaur')
