import sys
import socket
from functions import new_user, login, secure_drop

#########
# Start
#########
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#family, type
#he SOCK_STREAM means connection-oriented TCP protocol. 
print("Socket connection: success")
host = sys.argv[1] #local host
port = int(sys.argv[2]) #port number
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
#s.connect((host, port))
print("client has been assigned socket name: ", s.getsockname())


rec_msg = str()
msg = str()
if name == "main":


    s.connect((host, port))
        # get ip and port from "sys.argv[1]" and "sys.argv[2]"
   # connect to Server
    rec_msg == True
    while not rec_msg[0] == False:
        #msg = s.recv(1024)
        s.listen()
        msg = s.recv(port)
        msg .decode()
    # print

        # receive message from Server
            # validate
            # decrypt message
        # print rec_msg[1] to command line

        msg = input("input message: ")
        if msg == "exit":
            s.send(bytes(msg, "utf-8"))
            print("the server replied: "), msg.decode("utf-8")
        if msg == "exit":
            exit(1)
        else:
            s.send("...")

        # send new message to Server
            # if msg == "exit", break
            # else:
                # encrypt message
                # send message
    # gracefully close
    s.close()


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