import random
import string

alphabet = string.ascii_lowercase + string.digits


def get_random_string() -> str:
    return "".join(random.choices(alphabet, k=8))
