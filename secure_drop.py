import json
import socket
import sys
import functions as f
import fcrypt as fc


def login_loop()->list:
    while True:
        success, ret_user, email, full_name, password = f.login_client()
        if not success:
            print("Login Failed; Try Again.")
            continue
        else:
            # [success:bool, command:str, ret_user:bool, email:str, full_name:str, password:str]
            return [True, f.LOGIN_COM, ret_user, email, full_name, password]


def main_loop(username:str)->None:
    print('\nWelcome to SecureDrop')
    print('Type "help" For Commands')

    while True:
        command = input("\nsecure drop> ").lower()
        if command == "exit":
            print("Goodbye.")
            break
        if command in f.ACTION_LIST:
            match command:
                case "help":
                    msg = '\t"add" -> Add a new contact'
                    msg += '\n\t"list" -> List all online contacts'
                    msg += '\n\t"send" -> Transfer file to contact'
                    msg += '\n\t"exit" -> Exit SecureDrop'
                    print(msg)
                    continue
                case "add":
                    full_name, email = f.get_name_and_email()
                    s.send(bytes(json.dumps(["add", [email, full_name], username]), "utf-8"))
                case "list":
                    s.send(bytes(json.dumps(["list", [], username]), "utf-8"))
                case "send":
                    file_name = input("\tEnter file name, including path: ")
                    try:
                        fc.enc_dec(username, "encrypt", "private", file_name, "./file_to_send.bin")
                    except FileNotFoundError:
                        print("File Not Found.")
                    # TODO: finish
                    pass
        else:
            print("Command Not Recognized.")
            print('Type "help" For Commands')

        msg = s.recv(1024).decode("utf-8")
        print("pre-json.loads") # TODO:Delete
        print("msg:", msg) # TODO:Delete
        cont, json_msg = json.loads(msg)

        # print receied message to command line
        if not json_msg == "ping back":
            print(json_msg)

        if cont == False:
            print("Goodbye.")
            s.close()
            sys.exit(2)


#########
# Start #
#########
if __name__ == "__main__":
    database = {}
    database[f.USER] = {}

    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # family, type
        # The SOCK_STREAM means connection-oriented TCP protocol.
        print("Socket connection: success")
        host = sys.argv[1] # Server IP
        try:
            port = int(sys.argv[2]) # Server port number
        except ValueError:
            print("Port must be an Integer.")
            sys.exit(1)

        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        print("client has been assigned socket name: ", s.getsockname())

        # Login
        success, command, new, email, full_name, password = login_loop()
        if not success:
                print("Login Failed.")
                print("Goodbye.")
                s.close()
                sys.exit(1)

        user = [email, full_name]
        success2, msg = f.login_server(database, new, user, password)

        if not success2:
            print("Login Failed.")
            print("Goodbye.")
            s.close()
            sys.exit(1)

        # Connect to Server
        s.connect((host, port))

        main_loop(email)
        # s.send(bytes(json.dumps(["ping", [], None]), "utf-8"))

        # # msg_rec = [con't:bool, mesg:str]
        # cont, msg_rec = json.loads(s.recv(1024).decode("utf-8"))

        # if msg_rec == f.LOGIN_COM:
        #     success, command, new, email, full_name, password = login_loop()

        #     if not success:
        #         print("Login Failed.")
        #         print("Goodbye.")
        #         s.close()
        #         sys.exit(1)

        #     data = [new, [email, full_name], password]
        #     json_msg_out = json.dumps([command, data, email]).encode("utf-8")

        #     s.send(bytes(json_msg_out))

        #     main_loop(email)
        # else:
        #     email = f.get_email()
        #     s.send(bytes(json.dumps(["ping", [], None]), "utf-8"))
        #     main_loop(email)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("\nClient Crashing!")
        print(f"Exception: {e}")
    finally:
        print("\nClient Shutting Down.")
        s.close()
        sys.exit(0)
