from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib import messages

from .views import index, reset, remove, comparison_view
from .models import Pokemon, PokemonComparison


class ViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.session = {}
        self.user = AnonymousUser()

    def _get_post_request(self, path, **data):
        request = self.factory.post(path, data)

        request.session = self.session

        message_middleware = MessageMiddleware()
        message_middleware.process_request(request)

        request.user = self.user

        return request

    def _get_get_request(self, path, **data):
        request = self.factory.get(path, data)

        request.session = self.session

        message_middleware = MessageMiddleware()
        message_middleware.process_request(request)

        return request

    def _log_in(self, user):
        self.user = user
        if user.is_authenticated:
            self.session['_auth_user_id'] = user.id

    def _log_out(self):
        self.user = AnonymousUser()
        del self.session['_auth_user_id']


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

    def test_create_comparison_if_authenticated(self):
        user = User.objects.create(username='test')

        self._log_in(user)

        comparisons = PokemonComparison.objects.filter(user_id=user.id)

        self.assertEqual(len(comparisons), 0)

        request = self._get_post_request(
            '/', pokemon_set='1', pokemon_name='pikachu')

        response = index(request)

        self.assertEqual(response.status_code, 302)

        comparisons = PokemonComparison.objects.filter(user_id=user.id)

        self.assertEqual(len(comparisons), 1)

        comparisons[0].delete()

        self._log_out()

        user.delete()

    def test_do_not_create_comparison_if_not_authenticated(self):
        comparisons = PokemonComparison.objects.all()

        self.assertEqual(len(comparisons), 0)
        request = self._get_post_request(
            '/', pokemon_set='1', pokemon_name='pikachu')

        response = index(request)

        self.assertEqual(response.status_code, 302)

        comparisons = PokemonComparison.objects.all()

        self.assertEqual(len(comparisons), 0)

    def test_redirect_id_if_authenticated(self):
        user = User.objects.create(username='test')

        self._log_in(user)

        comparisons = PokemonComparison.objects.filter(user_id=user.id)

        self.assertEqual(len(comparisons), 0)

        request = self._get_post_request(
            '/', pokemon_set='1', pokemon_name='pikachu')

        response = index(request)

        self.assertEqual(response.status_code, 302)

        comparisons = PokemonComparison.objects.filter(user_id=user.id)

        self.assertEquals(len(comparisons), 1)

        comparison = comparisons[0]

        expected_path = '/comparison/{}'.format(comparison.id)

        self.assertTrue(
            expected_path in response.url,
            '{} not in {}'.format(expected_path, response.url))

        comparisons[0].delete()

        self._log_out()

        user.delete()


class ComparisonTest(ViewTestCase):

    def test_get_comparison(self):
        user = User.objects.create(username='test')

        self._log_in(user)

        request = self._get_post_request(
            '/', pokemon_set='1', pokemon_name='pikachu')
        index(request)

        self.session.clear()

        self._log_in(user)

        comparison = PokemonComparison.objects.all().first()

        request = self._get_get_request('comparison/{}'.format(comparison.id))

        response = comparison_view(request, comparison.id)

        self.assertEqual(response.status_code, 200)
        self.assertIn('pikachu', response.content.decode(response.charset))

        self._log_out()

        user.delete()


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
