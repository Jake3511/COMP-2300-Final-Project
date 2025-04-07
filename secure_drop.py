
# Move most of this to server

import sys
from functions import new_user, login, secure_drop

#########
# Start #
#########
if __name__ == "__main__":
    # connect to server
        # get ip and port from "sys.argv[1]" and "sys.argv[2]"
    # connect to Server
    # rec_msg == True
    # while not rec_msg[0] == False:
        # receive message from Server
            # validate
            # decrypt message
        # print rec_msg[1] to command line
        
        # send new message to Server
            # if msg == "exit", break
            # else:
                # encrypt message
                # send message
    # gracefully close


    pass

    # # Previous code:
    # # Empty database
    # database = {}
    # user_bool = False

    # while not user_bool:
    #     create_user = input("Do you want to register a new user (y/n)? ").lower()

    #     if not create_user in ["y", "yes"]:
    #         print("Goodbye")
    #         exit(0)
    #     user_bool = new_user(database)

    # if login(database):
    #     secure_drop(database)
