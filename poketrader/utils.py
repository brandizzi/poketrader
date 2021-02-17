def get_best_list(base_experience1, base_experience2):
    """
    Decices which list is the best betwen the two:

    >>> get_best_list(10, 20)
    'right'
    >>> get_best_list(20, 10)
    'left'

    If there is no best list, returns None:

    >>> get_best_list(10, 10) is None
    True
    """
    if base_experience1 > base_experience2:
        return 'left'
    elif base_experience2 > base_experience1:
        return 'right'
    else:
        return None


def as_percent(value):
    """
    Returns a value as a percentage, in a string:

    >>> as_percent(0.1)
    '10'
    """
    return '{:1.0f}'.format(value*100)
