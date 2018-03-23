import argparse

import CIM

parser = argparse.ArgumentParser(description="Admin interface for creating users from CSV files")

parser.add_argument("file", help="The file location to load")

args = parser.parse_args()

file = args.file

with open(file) as users:
    for line in users:
        username, password, perm = line.split(",")
        u = CIM.utils.db.new_user(username, password, perm)
        if u is None:
            print(f"Error creating user {username}, check the logs")
        else:
            print(f"Success creating user {username}")
