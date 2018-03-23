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
    if u is None:
        print("Error creating user! Please check logs for more details")
    else:
        print(f"User '{u}' created")

elif args.delete:
    print(f"Deleting user {user}")
    success = CIM.utils.db.del_user(user)
    if success:
        print(f"Successfully deleted user '{user}'")
    else:
        print(f"Error deleting user: User does not exist")

elif args.edit:
    new_pass = input("Enter New Password (Leave blank for no update): ")
    if new_pass == "":
        new_pass = None
    new_perm = input("Enter a new permission level (Leave blank for no update): ")
    if new_pass == "":
        new_perm = None
    r = CIM.utils.db.edit_user(user, new_pass, new_perm)
    if r is None:
        print("Error editing user")
    else:
        print("Succesfully updated user")

else:
    print(f"Retrieving information about {user}")
    u = CIM.utils.db.get_user(user)
    if u:
        print(f"Username: {u.usr}\nPassword: {u.passwd}\nPermission Level: {u.permlvl}")
    else:
        print(f"User '{user}' does not exist, cannot display information")
