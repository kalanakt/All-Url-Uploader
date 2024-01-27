import random
import string


def random_char(y):
    """
    Generate a random string of specified length.

    Parameters:
    - y (int): Length of the random string.

    Returns:
    str: Random string.
    """
    return "".join(random.choice(string.ascii_letters) for _ in range(y))