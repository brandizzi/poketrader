from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from .pokemon import fetch_pokemon, compare_pokemon_lists, APIException
from .utils import get_pokemon_lists, as_percent, get_best_list


def index(request):
    if request.method == 'POST':
        return handle_index_post_request(request)
    elif request.method == 'GET':
        return handle_index_get_request(request)


def reset(request):
    return handle_reset_post_request(request)


def remove(request):
    return handle_remove_post_request(request)


def handle_index_post_request(request):
    session = request.session

    pokemon_set = request.POST['pokemon_set']
    pokemon_name = request.POST['pokemon_name']

    try:
        pokemon = fetch_pokemon(pokemon_name)

        pokemon_list1, pokemon_list2 = get_pokemon_lists(session)

        if pokemon_set == '1':
            pokemon_list1.append(pokemon)
        elif pokemon_set == '2':
            pokemon_list2.append(pokemon)

        session['pokemon_list1'] = pokemon_list1
        session['pokemon_list2'] = pokemon_list2
    except APIException as e:
        messages.add_message(request, messages.ERROR, e.message)

    return HttpResponseRedirect('/')


def handle_index_get_request(request):
    pokemon_list1, pokemon_list2 = get_pokemon_lists(request.session)
    comp = compare_pokemon_lists(
        pokemon_list1, pokemon_list2, fairness_threshold=0.15)

    base_experience1 = comp['base_experience1']
    base_experience2 = comp['base_experience2']
    success = comp['success']
    difference = abs(comp['difference'])

    if success:
        unfairness = abs(comp['unfairness'])
        percentage = as_percent(unfairness)
    else:
        percentage = None

    return render(request, 'index.html', {
        'pokemon_list1': pokemon_list1, 'pokemon_list2': pokemon_list2,
        'base_experience1': base_experience1,
        'base_experience2': base_experience2, 'fair': comp['fair'],
        'difference': difference,
        'best_list': get_best_list(base_experience1, base_experience2),
        'percentage': percentage, 'success': success
    })


def handle_reset_post_request(request):
    session = request.session
    pokemon_set = request.POST['pokemon_set']
    pokemon_list = session.get('pokemon_list' + pokemon_set, [])
    pokemon_list.clear()
    session['pokemon_list' + pokemon_set] = pokemon_list
    return HttpResponseRedirect('/')


def handle_remove_post_request(request):
    session = request.session
    pokemon_set = request.POST['pokemon_set']
    pokemon_list = session.get('pokemon_list' + pokemon_set, [])
    index = int(request.POST['index'])
    del pokemon_list[index]
    session['pokemon_list' + pokemon_set] = pokemon_list
    return HttpResponseRedirect('/')
