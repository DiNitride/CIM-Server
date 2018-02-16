from random import choice
from string import ascii_letters, digits

TOKEN_LENGTH = 40


def generate_session_token():
    return "".join(choice(ascii_letters + digits) for i in range(TOKEN_LENGTH))
