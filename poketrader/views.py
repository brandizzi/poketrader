from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Pokemon, PokemonComparison
from .pokemon import fetch_pokemon, compare_pokemon_lists, APIException
from .utils import get_pokemon_lists, as_percent, get_best_list


def index(request):
    if request.method == 'POST':
        return handle_index_post_request(request)
    elif request.method == 'GET':
        return handle_index_get_request(request)


def comparison(request, comparison_id):
    if request.method == 'POST':
        return handle_comparison_post_request(request, comparison_id)
    elif request.method == 'GET':
        return handle_comparison_get_request(request, comparison_id)


def handle_comparison_get_request(request, comparison_id):
    if comparison_id is not None:
        comparison = get_object_or_404(PokemonComparison, id=comparison_id)
        pokemon_list1 = [p.as_dict() for p in comparison.list1.all()]
        pokemon_list2 = [p.as_dict() for p in comparison.list2.all()]
    else:
        pokemon_list1 = []
        pokemon_list2 = []
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

    return render(request, 'comparison.html', {
        'comparison_id': comparison_id if comparison_id is not None else '',
        'pokemon_list1': pokemon_list1, 'pokemon_list2': pokemon_list2,
        'base_experience1': base_experience1,
        'base_experience2': base_experience2, 'fair': comp['fair'],
        'difference': difference,
        'best_list': get_best_list(base_experience1, base_experience2),
        'percentage': percentage, 'success': success
    })


def reset(request):
    return handle_reset_post_request(request)


def remove(request):
    return handle_remove_post_request(request)


def handle_comparison_post_request(request, comparison_id):
    session = request.session

    pokemon_set = request.POST['pokemon_set']
    pokemon_name = request.POST['pokemon_name']
    redirect_url = '/'

    try:
        user = request.user
        comparison = None
        if user.is_authenticated and comparison_id is not None:
            comparison = PokemonComparison.objects.get(id=comparison_id)
            pokemon_list1 = [p.as_dict() for p in comparison.list1.all()]
            pokemon_list2 = [p.as_dict() for p in comparison.list2.all()]
        else:
            pokemon_list1, pokemon_list2 = get_pokemon_lists(session)

        pokemon = fetch_pokemon(pokemon_name)

        if pokemon_set == '1':
            pokemon_list1.append(pokemon)
        elif pokemon_set == '2':
            pokemon_list2.append(pokemon)

        session['pokemon_list1'] = pokemon_list1
        session['pokemon_list2'] = pokemon_list2

        Pokemon.objects.get_or_create(**pokemon)

        if user.is_authenticated:
            if comparison is None:
                comparison = PokemonComparison.objects.create(user=user)
            for p in pokemon_list1:
                comparison.list1.add(Pokemon.objects.get(name=p['name']))
            for p in pokemon_list2:
                comparison.list2.add(Pokemon.objects.get(name=p['name']))

            comparison.save()

            redirect_url = '/comparison/{}'.format(comparison.id)
    except APIException as e:
        messages.add_message(request, messages.ERROR, e.message)

    return HttpResponseRedirect(redirect_url)


@login_required
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

    return render(request, 'comparison.html', {
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
