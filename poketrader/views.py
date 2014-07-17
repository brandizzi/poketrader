from django.shortcuts import render
from django.http import HttpResponse

from .forms import PokemonForm

# Create your views here.


def index(request):
    form = PokemonForm()
    return render(request, 'index.html', {'form': form})
