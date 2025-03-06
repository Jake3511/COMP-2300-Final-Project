#!/usr/bin/python3

from functions import new_user, login, secure_drop

#########
# Start #
#########
if __name__ == "__main__":
    # Empty database
    database = {}
    user_bool = False

    while not user_bool:
        create_user = input("Do you want to register a new user (y/n)? ").lower()

        if not create_user in ["y", "yes"]:
            print("Goodbye")
            exit(0)
        user_bool = new_user(database)

    if login(database):
        secure_drop(database)
