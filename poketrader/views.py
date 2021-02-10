from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from .pokemon import fetch_pokemon


def index(request):
    if request.method == 'POST':
        return handle_index_post_request(request)
    elif request.method == 'GET':
        return handle_index_get_request(request)


def reset(request):
    return handle_reset_post_request(request)


def handle_index_post_request(request):
    session = request.session
    pokemon_list1, pokemon_list2 = get_pokemon_lists(session)

    pokemon_set = request.POST['pokemon_set']
    pokemon_name = request.POST['pokemon_name']
    pokemon = fetch_pokemon(pokemon_name)

    if pokemon_set == '1':
        pokemon_list1.append(pokemon)
    elif pokemon_set == '2':
        pokemon_list2.append(pokemon)

    session['pokemon_list1'] = pokemon_list1
    session['pokemon_list2'] = pokemon_list2

    return HttpResponseRedirect('/')


def handle_index_get_request(request):
    pokemon_list1, pokemon_list2 = get_pokemon_lists(request.session)

    return render(request, 'index.html', {
        'pokemon_list1': pokemon_list1, 'pokemon_list2': pokemon_list2
    })


def handle_reset_post_request(request):
    session = request.session
    pokemon_set = request.POST['pokemon_set']
    pokemon_list = session.get('pokemon_list' + pokemon_set, [])
    pokemon_list.clear()
    session['pokemon_list' + pokemon_set] = pokemon_list
    return HttpResponseRedirect('/')


def get_pokemon_lists(session):
    """
    Returns the two lists found in the session:

    >>> l1, l2 = get_pokemon_lists({
    ...     'pokemon_list1': ['pikachu'],
    ...     'pokemon_list2': ['charmander']
    ... })
    >>> l1
    ['pikachu']
    >>> l2
    ['charmander']
    """
    return (session.get('pokemon_list1', []), session.get('pokemon_list2', []))
