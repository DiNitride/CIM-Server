from random import choice
from string import ascii_letters, digits

# This is a constant value that should be consistent over all clients and the server
TOKEN_LENGTH = 40


def generate_session_token():
    """
    This function generates a random 40 character long session token for the client. It generates the token
    by randomly selecting an item from an array of letters and digits iteratively until the complete
    token has been generated.
    """
    return "".join(choice(ascii_letters + digits) for i in range(TOKEN_LENGTH))
