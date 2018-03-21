from enum import Enum
import psycopg2
import logging
import hashlib

from ..user import User
from . import tools

dbc = tools.load_config("db.json")

conn_str = f"host='{dbc['host']}' " \
           f"dbname='{dbc['db']}' " \
           f"user='{dbc['usr']}' " \
           f"password='{dbc['usr_pwd']}'"


logger = logging.getLogger(__name__)

conn = psycopg2.connect(conn_str)
cursor = conn.cursor()


class Login(Enum):
    """
    Small enumerator class to abstract the boolean value of whether a user is logged in into
    readable English words
    """
    AUTHORISED = True
    UNAUTHORISED = False


def new_user(usr: str, passwd: str, permlvl: int):
    """
    Create a new user in the database
    """
    # If the username has a . in, error because that is a disallowed character
    if "." in usr:
        logger.error("Unable to create user, '.' is a disallowed character")
        return
    # Get any users with that username already
    cursor.execute("SELECT * FROM public.users WHERE login=(%s)", (usr,))
    user_list = cursor.fetchall()
    if len(user_list) != 0:
        # If there are any users with that name, throw an error
        logger.error(f"Error creating user '{usr}': Already exists in table")
        return
    # Hash the provided password for security
    passwd = hashlib.sha256(passwd.encode()).hexdigest()
    # Insert user into DB
    cursor.execute("INSERT INTO public.users VALUES (%s, %s, %s)", (usr, passwd, permlvl))
    conn.commit()
    logger.info(f"Successfully created new user '{usr}'")
    return get_user(usr)


def del_user(usr: str):
    """
    Delete a user from the DB
    """
    # Check the user exists first
    if get_user(usr) is not None:
        # Execute SQL
        cursor.execute("DELETE FROM public.users WHERE login=(%s)", (usr,))
        conn.commit()
        logger.info(f"Successfully deleted user '{usr}'")
        return True
    else:
        logger.error(f"Error deleting user '{usr}': User does not exist")
        return False


def get_user(usr: str):
    """
    Retrieve a user from the database
    """
    # Execute SQL
    cursor.execute("SELECT * FROM public.users WHERE login=(%s)", (usr,))
    u = cursor.fetchone()
    if u is not None:
        # Create a new user object to return
        user = User(*u)
        return user
    return None


def check_authorise_user(username, password):
    """
    Authorise a user with a given username and password
    """
    user = get_user(username)
    if user is not None:
        if user.passwd == password:
            return Login.AUTHORISED
    return Login.UNAUTHORISED
