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
