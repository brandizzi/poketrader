from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from .pokemon import fetch_pokemon


def index(request):
    session = request.session
    pokemon_list1 = session.get('pokemon_list1', [])
    pokemon_list2 = session.get('pokemon_list2', [])

    if request.method == 'POST':
        pokemon_set = request.POST['pokemon_set']
        pokemon_name = request.POST['pokemon_name']
        pokemon = fetch_pokemon(pokemon_name)

        if pokemon_set == '1':
            pokemon_list1.append(pokemon)
        elif pokemon_set == '2':
            pokemon_list2.append(pokemon)

        session['pokemon_list1'] = pokemon_list1
        session['pokemon_list2'] = pokemon_list2

    return render(request, 'index.html', {'pokemon_list1': pokemon_list1, 'pokemon_list2': pokemon_list2})


def reset(request):
    session = request.session
    pokemon_set = request.POST['pokemon_set']
    pokemon_list = session.get('pokemon_list' + pokemon_set, [])
    pokemon_list.clear()
    session['pokemon_list' + pokemon_set] = pokemon_list
    return HttpResponseRedirect('/')
