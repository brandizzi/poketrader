"""
This module contains the Pokemon class (to represent pokémons) as well as the
fetch_pokemon() function to retrieve pokémons.
"""

import pokepy

CLIENT = pokepy.V2Client()


def fetch_pokemon(name):
    """
    This function retrieves data from the PokéAPI and returns
    an instance of our class Pokemon with the relevant part of
    the data.

    If I request, for example, data about pikachu...

    >>> pokemon = fetch_pokemon('pikachu')

    ...my Pokemon instance will have the relevant data for
    dispaying and comparing pokémon deals:

    >>> pokemon
    {'name': 'pikachu', 'base_experience': 112, 'picture_url': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png'}
    """
    api_pokemon = CLIENT.get_pokemon(name)

    return {
        'name': api_pokemon.name,
        'base_experience': api_pokemon.base_experience,
        'picture_url': api_pokemon.sprites.front_default
    }


def compare_pokemon_lists(list1, list2, fairness_threshold=0.1):
    """
    Compare two pokémon lists to report whether it woud be fair to follow with
    an exchange.

    Let's suppose we have such two lists:

    >>> list1 = [
    ...     {
    ...         'name': 'pikachu',
    ...         'base_experience' : 112,
    ...         'picture_url': '...'
    ...     },
    ...     {
    ...         'name': 'ditto',
    ...         'base_experience' : 101,
    ...         'picture_url': '...'
    ...     }
    ... ]
    >>> list2 = [
    ...     {
    ...         'name': 'bulbasaur',
    ...         'base_experience' : 64,
    ...         'picture_url': '...'
    ...     },
    ...     {
    ...         'name': 'charmander',
    ...         'base_experience' : 62,
    ...         'picture_url': '...'
    ...     }
    ... ]

    compare_pokemon_lists() will return a dictionary reporting the total base
    experience of both lists, the difference between them and the percentage
    this difference is of the least experienced list, which we arbitrarily
    define as being the "unfairness factor." It will also report if the exchange
    is "fair":

    >>> compare_pokemon_lists(list1, list2)                # doctest: +ELLIPSIS
    {'base_experience1': 213, 'base_experience2': 126, 'difference': 87, 'unfairness': 0.69..., 'fair': False}
    >>> compare_pokemon_lists(list2, list1)                # doctest: +ELLIPSIS
    {'base_experience1': 126, 'base_experience2': 213, 'difference': -87, 'unfairness': 0.69..., 'fair': False}

    By default, the transaction is deemed "fair" if the fairness factor is
    smaller or equal to 10%. It can be changed, though:

    >>> compare_pokemon_lists(                             # doctest: +ELLIPSIS
    ...     list1, list2, fairness_threshold=0.7)
    {'base_experience1': 213, 'base_experience2': 126, 'difference': 87, 'unfairness': 0.69..., 'fair': True}

    """
    base_experience1 = sum(p['base_experience'] for p in list1)
    base_experience2 = sum(p['base_experience'] for p in list2)
    difference = base_experience1 - base_experience2
    smaller_base_experience = min(base_experience1, base_experience2)
    fairness = abs(difference) / smaller_base_experience

    return {
        'base_experience1': base_experience1,
        'base_experience2': base_experience2,
        'difference': difference,
        'unfairness': fairness,
        'fair': fairness <= fairness_threshold
    }
