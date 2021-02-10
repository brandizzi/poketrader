from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def index(request):
    session = request.session
    pokemon_list1 = session.get('pokemon_list1', [])
    pokemon_list2 = session.get('pokemon_list2', [])

    if request.method == 'POST':
        pokemon_set = request.POST['pokemon_set']
        pokemon_name = request.POST['pokemon_name']
        if pokemon_set == '1':
            pokemon_list1.append(pokemon_name)
        elif pokemon_set == '2':
            pokemon_list2.append(pokemon_name)

        session['pokemon_list1'] = pokemon_list1
        session['pokemon_list2'] = pokemon_list2

    return render(request, 'index.html', {'pokemon_list1': pokemon_list1, 'pokemon_list2': pokemon_list2})
