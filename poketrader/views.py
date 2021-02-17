from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import (
    require_GET, require_POST, require_http_methods)

from .models import Pokemon, PokemonComparison
from .pokemon import fetch_pokemon, compare_pokemon_lists, APIException
from .utils import as_percent, get_best_list


@login_required
@require_GET
def index(request):
    comparisons = PokemonComparison.objects.filter(user=request.user)

    return render(request, 'index.html', {
        'comparisons': comparisons
    })


@login_required
@require_http_methods(['GET', 'POST'])
def comparison(request, comparison_id):
    if request.method == 'POST':
        return handle_comparison_post_request(request, comparison_id)
    elif request.method == 'GET':
        return handle_comparison_get_request(request, comparison_id)


@login_required
@require_POST
def reset(request, comparison_id):
    pokemon_set = request.POST['pokemon_set']
    comparison = get_object_or_404(PokemonComparison, id=comparison_id)

    if pokemon_set == '1':
        comparison.list1.clear()
    elif pokemon_set == '2':
        comparison.list2.clear()

    return HttpResponseRedirect('/comparison/{}'.format(comparison_id))


@login_required
@require_POST
def remove(request, comparison_id):
    pokemon_set = request.POST['pokemon_set']
    index = int(request.POST['index'])
    comparison = get_object_or_404(PokemonComparison, id=comparison_id)

    if pokemon_set == '1':
        list = comparison.list1
    elif pokemon_set == '2':
        list = comparison.list2

    list.remove(list.all()[index])

    return HttpResponseRedirect('/comparison/{}'.format(comparison_id))


@login_required
@require_POST
def delete(request, comparison_id):
    comparison = get_object_or_404(PokemonComparison, id=comparison_id)
    comparison.delete()

    messages.add_message(
        request, messages.INFO, 'Comparison deleted.', extra_tags='success')

    return HttpResponseRedirect('/')


def handle_comparison_get_request(request, comparison_id):
    pokemon_list1 = []
    pokemon_list2 = []

    if comparison_id is not None:
        comparison = get_object_or_404(PokemonComparison, id=comparison_id)
        pokemon_list1, pokemon_list2 = comparison.as_list_of_dicts()

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


def handle_comparison_post_request(request, comparison_id):
    pokemon_set = request.POST['pokemon_set']
    pokemon_name = request.POST['pokemon_name']

    user = request.user
    if comparison_id is not None:
        comparison = get_object_or_404(PokemonComparison, id=comparison_id)
    else:
        comparison = PokemonComparison.objects.create(user=user)

    try:
        pokemon, _ = Pokemon.objects.get_or_create(
            name=pokemon_name, defaults=fetch_pokemon(pokemon_name))

        if pokemon_set == '1':
            comparison.list1.add(pokemon)
        elif pokemon_set == '2':
            comparison.list2.add(pokemon)

        comparison.save()
    except APIException as e:
        messages.add_message(
            request, messages.ERROR, e.message, extra_tags='danger')

    redirect_url = '/comparison/{}'.format(comparison.id)
    return HttpResponseRedirect(redirect_url)
