"""
This module contains the Pokemon class (to represent pokémons) as well as the
fetch_pokemon() function to retrieve pokémons.
"""
import functools

import pokepy

CLIENT = pokepy.V2Client()


@functools.lru_cache(maxsize=512)
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

    Note that this function is case-insensitive and ignores any trailing spaces
    in the name of the pokémon:

    >>> fetch_pokemon('BuLbAsAuR')
    {'name': 'bulbasaur', 'base_experience': 64, 'picture_url': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png'}
    >>> fetch_pokemon('    charmander      ')
    {'name': 'charmander', 'base_experience': 62, 'picture_url': 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png'}

    If the requested Pokémon does not exist, raise an APIException:

    >>> pokemon = fetch_pokemon('agumon')
    Traceback (most recent call last):
     ...
    pokemon.APIException: There is no such Pokémon called "agumon."
    >>> pokemon = fetch_pokemon('flamedramon')
    Traceback (most recent call last):
      ...
    pokemon.APIException: There is no such Pokémon called "flamedramon."

    """
    try:
        api_pokemon = CLIENT.get_pokemon(name.strip())
    except:
        raise APIException(
            "There is no such Pokémon called \"{}.\"".format(name))

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
    {'base_experience1': 213, 'base_experience2': 126, 'difference': 87, 'unfairness': 0.69..., 'fair': False, 'success': True}
    >>> compare_pokemon_lists(list2, list1)                # doctest: +ELLIPSIS
    {'base_experience1': 126, 'base_experience2': 213, 'difference': -87, 'unfairness': 0.69..., 'fair': False, 'success': True}

    By default, the transaction is deemed "fair" if the fairness factor is
    smaller or equal to 10%. It can be changed, though:

    >>> compare_pokemon_lists(                             # doctest: +ELLIPSIS
    ...     list1, list2, fairness_threshold=0.7)
    {'base_experience1': 213, 'base_experience2': 126, 'difference': 87, 'unfairness': 0.69..., 'fair': True, 'success': True}


    Note that there is a "success" flag. If one of the lists is empty, or
    somehow its total base experience is less than or equal to 0, then success
    will be false:

    >>> compare_pokemon_lists([], list2)                # doctest: +ELLIPSIS
    {'base_experience1': 0, 'base_experience2': 126, 'difference': -126, 'unfairness': nan, 'fair': False, 'success': False}

    """
    base_experience1 = sum(p['base_experience'] for p in list1)
    base_experience2 = sum(p['base_experience'] for p in list2)
    success = base_experience1 > 0 and base_experience2 > 0
    difference = base_experience1 - base_experience2
    smaller_base_experience = min(base_experience1, base_experience2)

    if success:
        fairness = abs(difference) / smaller_base_experience
    else:
        fairness = float('NaN')

    return {
        'base_experience1': base_experience1,
        'base_experience2': base_experience2,
        'difference': difference,
        'unfairness': fairness,
        'fair': fairness <= fairness_threshold,
        'success': success
    }


class APIException(Exception):
    """
    Exception to be raised when a call to PokeAPI fails.
    """

    def __init__(self, message, *args, **kwargs):
        super().__init__(*(message, *args), **kwargs)
        self.message = message
