"""
Extremely rudimentary admin management application.
This will be expanding into with more features later down the line,
however for now it serves as a debugging tool.
"""

import argparse

import CIM

parser = argparse.ArgumentParser(description="Admin interface for managing CIM Server")

parser.add_argument("user", help="The username to view or modify")
group = parser.add_mutually_exclusive_group()
group.add_argument("-a", "--add", help="Create a user", action="store_true")
group.add_argument("-d", "--delete", help="Delete a user", action="store_true")
group.add_argument("-e", "--edit", help="Modify a user", action="store_true")

args = parser.parse_args()

user = args.user

if args.add:
    if CIM.utils.db.get_user(user):
        print(f"Unable to create new user with name '{user}', already exists!\nPlease delete or edit that user")
        exit(0)
    passwd = input(f"User '{user}' password: ")
    perm = int(input(f"User '{user}' permission level: "))
    u = CIM.utils.db.new_user(user, passwd, perm)
    print(f"User '{u}' created")
elif args.delete:
    print(f"Deleting user {user}")
    success = CIM.utils.db.del_user(user)
    if success:
        print(f"Successfully deleted user '{user}'")
    else:
        print(f"Error deleting user '{usr}': User does not exist")
elif args.edit:
    print(f"Feature not enabled")
else:
    print(f"Retrieving information about {user}")
    u = CIM.utils.db.get_user(user)
    if u:
        print(f"Username: {u.usr}\nPassword: {u.passwd}\nPermission Level: {u.permlvl}")
    else:
        print(f"User '{user}' does not exist, cannot display information")
