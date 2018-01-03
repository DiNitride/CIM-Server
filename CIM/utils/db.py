import psycopg2
import logging

from ..user import User
from . import tools

# database config
dbc = tools.load_config("db.json")

conn_str = f"host='{dbc['host']}' " \
           f"dbname='{dbc['db']}' " \
           f"user='{dbc['usr']}' " \
           f"password='{dbc['usr_pwd']}'"

conn = psycopg2.connect(conn_str)
cursor = conn.cursor()

logger = logging.getLogger(__name__)


def new_user(usr: str, passwd: str, permlvl: int):
    cursor.execute("SELECT * FROM public.users WHERE login=(%s)", (usr,))
    user_list = cursor.fetchall()
    if len(user_list) != 0:
        logger.error(f"Error creating user '{usr}': Already exists in table")
        return
    cursor.execute("INSERT INTO public.users VALUES (%s, %s, %s)", (usr, passwd, permlvl))
    conn.commit()
    logger.info(f"Successfully created new user '{usr}'")


def del_user(usr: str):
    if get_user(usr) is not None:
        cursor.execute("DELETE FROM public.users WHERE login=(%s)", (usr,))
        conn.commit()
        logger.info(f"Successfully deleted user '{usr}'")
    else:
        logger.error(f"Error deleting user '{usr}': User does not exist")


def get_user(usr: str):
    cursor.execute("SELECT * FROM public.users WHERE login=(%s)", (usr,))
    u = cursor.fetchone()
    if u is not None:
        user = User(*u)
        return user
    return u
