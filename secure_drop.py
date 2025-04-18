import json
import socket
import sys
import functions as f
import fcrypt as fc


ACTION_LIST = ["help", "add", "list", "send", "exit"]


def login_loop():
    while True:
        success, ret_user, email, full_name, password = f.login_client()
        if not success:
            print("Login Failed; Try Again.")
            continue
        else:
            # [logged_in:bool, command:str, data:list]
            return [False, "login", [ret_user, [email, full_name], password]]


def main_loop(username:str)->None:
    print('Welcome to SecureDrop')
    print('Type "help" For Commands')

    while True:
        msg = s.recv(1024).decode("utf-8")
        json_msg = json.loads(msg)

        # print rec_msg[1] to command line
        print(json_msg[1])

        if json_msg[0] == False:
            print("Goodbye.")
            sys.exit(2)


        # receive message from Server
            # validate
            # decrypt message

        while True:
            command = input("secure drop> ").lower()
            if command == "exit":
                print("Goodbye.")
                exit(0)
            if command in ACTION_LIST:
                match command:
                    case "help":
                        msg = '\t"add" -> Add a new contact'
                        msg += '\n\t"list" -> List all online contacts'
                        msg += '\n\t"send" -> Transfer file to contact'
                        msg += '\n\t"exit" -> Exit SecureDrop'
                        print(msg)
                    case "add":
                        full_name, email = f.get_name_and_email()
                        s.send(bytes([True, "add", [email, full_name]]))
                    case "list":
                        s.send(bytes([True, "list", []]))
                    case "send":
                        file_name = input("\tEnter file name, including path")
                        fc.enc_dec(username, "encrypt", "private", file_name, "./file_to_send.bin")
                        # TODO: finish
                        pass
            else:
                print("Command Not Recognized.")
                print('Type "help" For Commands')


#########
# Start #
#########
if __name__ == "__main__":
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #family, type
    #he SOCK_STREAM means connection-oriented TCP protocol.
    print("Socket connection: success")
    host = sys.argv[1] #local host
    try:
        port = int(sys.argv[2]) #port number
    except ValueError:
        print("Port must be an Integer.")
        sys.exit(1)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    print("client has been assigned socket name: ", s.getsockname())

    s.connect((host, port))
    # connect to Server

    # msg  = [logged_in:bool, command:str, [ret_user, [email, full_name], password]]
    msg = login_loop()

    email = msg[2][1][0]

    json_msg = json.dumps(msg)


    s.send(bytes(json_msg.encode("utf-8")))

    main_loop(email)

    s.close()
