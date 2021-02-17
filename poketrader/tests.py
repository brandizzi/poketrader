import contextlib

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib import messages

from .views import (
    index as index_view, reset as reset_view, remove as remove_view,
    comparison as comparison_view, delete as delete_view)
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

    def fetch_and_save_pokemon(self, name, comparison=None):
        request = self.get_post_request(
            '/comparison', pokemon_set='1', pokemon_name=name)

        return comparison_view(
            request, comparison.id if comparison is not None else None)

    def assertRedirect(self, response, url):
        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            url in response.url, '{} not in {}'.format(url, response.url))

    @contextlib.contextmanager
    def logged_in(self):
        user = User.objects.create(username='test')

        try:
            self.log_in(user)
            yield user
        finally:
            self.log_out()

            user.delete()

    def get_comparison(self, user):
        return PokemonComparison.objects.get(user=user)

    def _set_up_request(self, request):
        request.session = self.session

        message_middleware = MessageMiddleware()
        message_middleware.process_request(request)

        request.user = self.user


class ComparisonPostViewTest(ViewTestCase):

    def test_save_to_database(self):
        with self.logged_in() as user:
            pokemons = Pokemon.objects.filter(name='pikachu')

            self.assertEqual(len(pokemons), 0)

            request = self.get_post_request(
                '/comparison', pokemon_set='1', pokemon_name='pikachu')

            response = comparison_view(request, None)

            self.assertEqual(response.status_code, 302)

            pokemons = Pokemon.objects.filter(name='pikachu')

            self.assertEqual(len(pokemons), 1)

            pokemons[0].delete()

    def test_no_more_data_in_session(self):
        request = self.get_post_request(
            '/comparison', pokemon_set='1', pokemon_name='pikachu')

        response = comparison_view(request, None)

        self.assertEqual(response.status_code, 302)

        list1 = request.session.get('pokemon_list1', [])
        self.assertEqual(len(list1), 0)

    def test_pokemon_not_found(self):
        with self.logged_in() as user:
            request = self.get_post_request(
                '/comparison', pokemon_set='1', pokemon_name='agumon')

            response = comparison_view(request, None)

            self.assertRedirect(response, '/comparison')

            messages_list = list(messages.get_messages(request))

            self.assertEqual(len(messages_list), 1)
            self.assertEqual(
                messages_list[0].message,
                "There is no such Pokémon called \"agumon.\"")

    def test_index_multiple(self):
        with self.logged_in() as user:
            request = self.get_post_request(
                '/comparison', pokemon_set='1', pokemon_name='pikachu')
            comparison_view(request, None)
            comparison = self.get_comparison(user)

            request = self.get_post_request(
                '/comparison', pokemon_set='1', pokemon_name='charmander')
            comparison_view(request, comparison.id)

            request = self.get_post_request(
                '/comparison', pokemon_set='1', pokemon_name='bulbasaur')
            comparison_view(request, comparison.id)

            comparison = self.get_comparison(user)
            self.assertEqual(len(comparison.list1), 3)

    def test_create_comparison_if_authenticated(self):
        with self.logged_in() as user:
            comparisons = PokemonComparison.objects.filter(user_id=user.id)

            self.assertEqual(len(comparisons), 0)

            response = self.fetch_and_save_pokemon('pikachu')

            self.assertEqual(response.status_code, 302)

            comparisons = PokemonComparison.objects.filter(user_id=user.id)

            self.assertEqual(len(comparisons), 1)

            comparisons[0].delete()

    def test_do_not_create_comparison_if_not_authenticated(self):
        comparisons = PokemonComparison.objects.all()

        self.assertEqual(len(comparisons), 0)

        response = self.fetch_and_save_pokemon('pikachu')

        self.assertEqual(response.status_code, 302)

        comparisons = PokemonComparison.objects.all()

        self.assertEqual(len(comparisons), 0)

    def test_update_comparison(self):
        with self.logged_in() as user:
            comparisons = PokemonComparison.objects.filter(user_id=user.id)

            self.assertEqual(len(comparisons), 0)

            self.fetch_and_save_pokemon('pikachu')

            comparison = PokemonComparison.objects.get(user_id=user.id)

            self.assertEqual(len(comparison.list1), 1)

            request = self.get_post_request(
                '/comparison/{}'.format(comparison.id), pokemon_set='1',
                pokemon_name='charmander')

            comparison_view(request, comparison.id)

            comparison = PokemonComparison.objects.get(user_id=user.id)

            self.assertEqual(len(comparison.list1), 2)

            comparisons.delete()

    def test_update_comparison_repeating_pokemon(self):
        with self.logged_in() as user:
            comparisons = PokemonComparison.objects.filter(user_id=user.id)

            self.assertEqual(len(comparisons), 0)

            self.fetch_and_save_pokemon('pikachu')

            comparison = PokemonComparison.objects.get(user_id=user.id)

            self.assertEqual(len(comparison.list1), 1)

            request = self.get_post_request(
                '/comparison/{}'.format(comparison.id), pokemon_set='1',
                pokemon_name='pikachu')

            comparison_view(request, comparison.id)

            comparison = PokemonComparison.objects.get(user_id=user.id)

            self.assertEqual(len(comparison.list1), 2)

            comparisons.delete()

    def test_redirect_id_if_authenticated(self):
        with self.logged_in() as user:
            comparisons = PokemonComparison.objects.filter(user_id=user.id)

            self.assertEqual(len(comparisons), 0)

            response = self.fetch_and_save_pokemon('pikachu')

            comparisons = PokemonComparison.objects.filter(user_id=user.id)

            self.assertEquals(len(comparisons), 1)

            comparison = comparisons[0]

            expected_path = '/comparison/{}'.format(comparison.id)

            self.assertRedirect(response, expected_path)

            comparisons[0].delete()


class IndexGetViewTest(ViewTestCase):

    def test_get_page(self):
        with self.logged_in() as user:
            request = self.get_get_request('/')

            response = index_view(request)

            self.assertEqual(response.status_code, 200)

            list1 = request.session.get('pokemon_list1', [])

            self.assertEqual(len(list1), 0)

    def test_get_page_lists_comparisons(self):
        with self.logged_in() as user:
            self.fetch_and_save_pokemon('pikachu')

            comparison = PokemonComparison.objects.get(user_id=user.id)

            request = self.get_post_request(
                '/comparison/{}'.format(comparison.id), pokemon_set='1',
                pokemon_name='charmander')

            comparison_view(request, comparison.id)

            self.fetch_and_save_pokemon('bulbasaur')

            request = self.get_get_request('/')

            response = index_view(request)

            content = response.content.decode(response.charset)
            self.assertIn('pikachu', content)
            self.assertIn('charmander', content)
            self.assertIn('bulbasaur', content)

    def test_get_page_redirect_unauthenticated(self):
        request = self.get_get_request('/')

        response = index_view(request)

        self.assertRedirect(response, '/login')


class ComparisonViewTest(ViewTestCase):

    def test_get_comparison(self):
        with self.logged_in() as user:
            response = self.fetch_and_save_pokemon('pikachu')

            comparison = PokemonComparison.objects.all().first()

            request = self.get_get_request(
                'comparison/{}'.format(comparison.id))

            response = comparison_view(request, comparison.id)

            self.assertEqual(response.status_code, 200)
            self.assertIn('pikachu', response.content.decode(response.charset))

    def test_get_page_redirect_unauthenticated(self):
        request = self.get_get_request('comparison')

        response = comparison_view(request, None)

        self.assertRedirect(response, '/login')


class ResetViewTest(ViewTestCase):

    def test_reset_session(self):
        with self.logged_in() as user:
            response = self.fetch_and_save_pokemon('pikachu')

            comparison = self.get_comparison(user)
            self.assertEqual(len(comparison.list1), 1)

            request = self.get_post_request('/reset', pokemon_set='1')

            response = reset_view(request, comparison.id)

            self.assertEqual(response.status_code, 302)

            comparison = self.get_comparison(user)
            self.assertEqual(len(comparison.list1), 0)

    def test_get_page_redirect_unauthenticated(self):
        with self.logged_in() as user:
            response = self.fetch_and_save_pokemon('pikachu')

            comparison = PokemonComparison.objects.all().first()

        request = self.get_get_request('comparison/{}'.format(comparison.id))

        self.assertRedirect(response, '/login')

    def test_get_page_redirect_unauthenticated(self):
        request = self.get_get_request('reset/1')

        response = reset_view(request, None)

        self.assertRedirect(response, '/login')


class RemoveViewTest(ViewTestCase):

    def test_remove_pokemon(self):
        with self.logged_in() as user:
            response = self.fetch_and_save_pokemon('pikachu')
            comparison = self.get_comparison(user)
            response = self.fetch_and_save_pokemon('charmander', comparison)
            response = self.fetch_and_save_pokemon('bulbasaur', comparison)

            comparison = self.get_comparison(user)
            self.assertEqual(len(comparison.list1), 3)

            request = self.get_post_request(
                '/remove', pokemon_set='1', index='1')

            response = remove_view(request, comparison.id)

            self.assertEqual(response.status_code, 302)

            comparison = self.get_comparison(user)
            self.assertEqual(len(comparison.list1), 2)
            self.assertEqual(comparison.list1[0].name, 'pikachu')
            self.assertEqual(comparison.list1[1].name, 'bulbasaur')

    def test_get_page_redirect_unauthenticated(self):
        request = self.get_get_request('remove/1')

        response = remove_view(request, None)

        self.assertRedirect(response, '/login')


class DeleteViewTest(ViewTestCase):

    def test_delete_comparison(self):
        with self.logged_in() as user:
            response = self.fetch_and_save_pokemon('pikachu')
            comparison = self.get_comparison(user)

            comparison = self.get_comparison(user)
            self.assertEqual(len(comparison.list1), 1)

            request = self.get_post_request(
                '/delete', pokemon_set='1', index='1')

            response = delete_view(request, comparison.id)

            with self.assertRaises(Exception):
                comparison = self.get_comparison(user)

    def test_get_page_redirect_unauthenticated(self):
        request = self.get_get_request('remove/1')

        response = delete_view(request, None)

        self.assertRedirect(response, '/login')
