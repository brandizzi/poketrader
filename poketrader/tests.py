from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib import messages

from .views import (
    index as index_view, reset as reset_view, remove as remove_view,
    comparison as comparison_view)
from .models import Pokemon, PokemonComparison


class ViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.session = {}
        self.user = AnonymousUser()

    def get_post_request(self, path, **data):
        request = self.factory.post(path, data)

        self._set_up_request(request)

        return request

    def get_get_request(self, path, **data):
        request = self.factory.get(path, data)

        self._set_up_request(request)

        return request

    def log_in(self, user):
        self.user = user
        if user.is_authenticated:
            self.session['_auth_user_id'] = user.id

    def log_out(self):
        self.user = AnonymousUser()
        del self.session['_auth_user_id']

    def fetch_and_save_pokemon(self, name):
        request = self.get_post_request(
            '/', pokemon_set='1', pokemon_name=name)

        return index_view(request)

    def assertRedirect(self, response, url):
        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            url, '{} not in {}'.format(url, response.url))

    def _set_up_request(self, request):
        request.session = self.session

        message_middleware = MessageMiddleware()
        message_middleware.process_request(request)

        request.user = self.user


class IndexPostViewTest(ViewTestCase):

    def test_save_to_database(self):
        pokemons = Pokemon.objects.filter(name='pikachu')

        self.assertEqual(len(pokemons), 0)

        request = self.get_post_request(
            '/', pokemon_set='1', pokemon_name='pikachu')

        response = index_view(request)

        self.assertEqual(response.status_code, 302)

        pokemons = Pokemon.objects.filter(name='pikachu')

        self.assertEqual(len(pokemons), 1)

        pokemons[0].delete()

    def test_add_to_session(self):
        request = self.get_post_request(
            '/', pokemon_set='1', pokemon_name='pikachu')

        response = index_view(request)

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
        request = self.get_post_request(
            '/', pokemon_set='1', pokemon_name='agumon')

        response = index_view(request)

        self.assertEqual(response.status_code, 302)

        list1 = request.session.get('pokemon_list1', [])
        self.assertEqual(len(list1), 0)

        messages_list = list(messages.get_messages(request))

        self.assertEqual(len(messages_list), 1)
        self.assertEqual(
            messages_list[0].message,
            "There is no such Pokémon called \"agumon.\"")

    def test_index_multiple(self):
        request = self.get_post_request(
            '/', pokemon_set='1', pokemon_name='pikachu')
        index_view(request)

        request = self.get_post_request(
            '/', pokemon_set='1', pokemon_name='charmander')
        index_view(request)

        request = self.get_post_request(
            '/', pokemon_set='1', pokemon_name='bulbasaur')
        index_view(request)

        list1 = request.session['pokemon_list1']
        self.assertEqual(len(list1), 3)

    def test_create_comparison_if_authenticated(self):
        user = User.objects.create(username='test')

        self.log_in(user)

        comparisons = PokemonComparison.objects.filter(user_id=user.id)

        self.assertEqual(len(comparisons), 0)

        response = self.fetch_and_save_pokemon('pikachu')

        self.assertEqual(response.status_code, 302)

        comparisons = PokemonComparison.objects.filter(user_id=user.id)

        self.assertEqual(len(comparisons), 1)

        comparisons[0].delete()

        self.log_out()

        user.delete()

    def test_do_not_create_comparison_if_not_authenticated(self):
        comparisons = PokemonComparison.objects.all()

        self.assertEqual(len(comparisons), 0)

        response = self.fetch_and_save_pokemon('pikachu')

        self.assertEqual(response.status_code, 302)

        comparisons = PokemonComparison.objects.all()

        self.assertEqual(len(comparisons), 0)

    def test_redirect_id_if_authenticated(self):
        user = User.objects.create(username='test')

        self.log_in(user)

        comparisons = PokemonComparison.objects.filter(user_id=user.id)

        self.assertEqual(len(comparisons), 0)

        response = self.fetch_and_save_pokemon('pikachu')

        comparisons = PokemonComparison.objects.filter(user_id=user.id)

        self.assertEquals(len(comparisons), 1)

        comparison = comparisons[0]

        expected_path = '/comparison/{}'.format(comparison.id)

        self.assertRedirect(response, expected_path)

        comparisons[0].delete()

        self.log_out()

        user.delete()


class IndexGetViewTest(ViewTestCase):

    def test_get_page(self):
        request = self.get_get_request('/')

        response = index_view(request)

        self.assertEqual(response.status_code, 200)

        list1 = request.session.get('pokemon_list1', [])

        self.assertEqual(len(list1), 0)


class ComparisonViewTest(ViewTestCase):

    def test_get_comparison(self):
        user = User.objects.create(username='test')

        self.log_in(user)

        response = self.fetch_and_save_pokemon('pikachu')

        self.session.clear()

        self.log_in(user)

        comparison = PokemonComparison.objects.all().first()

        request = self.get_get_request('comparison/{}'.format(comparison.id))

        response = comparison_view(request, comparison.id)

        self.assertEqual(response.status_code, 200)
        self.assertIn('pikachu', response.content.decode(response.charset))

        self.log_out()

        user.delete()


class ResetViewTest(ViewTestCase):

    def test_reset_session(self):
        response = self.fetch_and_save_pokemon('pikachu')

        list1 = self.session['pokemon_list1']
        self.assertEqual(len(list1), 1)

        request = self.get_post_request('/reset', pokemon_set='1')

        response = reset_view(request)

        self.assertEqual(response.status_code, 302)

        list1 = request.session['pokemon_list1']
        self.assertEqual(len(list1), 0)


class RemoveViewTest(ViewTestCase):

    def test_remove_pokemon(self):
        response = self.fetch_and_save_pokemon('pikachu')

        response = self.fetch_and_save_pokemon('charmander')

        response = self.fetch_and_save_pokemon('bulbasaur')

        list1 = self.session['pokemon_list1']
        self.assertEqual(len(list1), 3)

        request = self.get_post_request('/remove', pokemon_set='1', index='1')

        response = remove_view(request)

        self.assertEqual(response.status_code, 302)

        list1 = self.session['pokemon_list1']
        self.assertEqual(len(list1), 2)
        self.assertEqual(list1[0]['name'], 'pikachu')
        self.assertEqual(list1[1]['name'], 'bulbasaur')
