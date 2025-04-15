import sys
import socket
import functions as f
import fcrypt


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




def main_loop():
    print('Welcome to SecureDrop')
    print('Type "help" For Commands')

    while True:
        s.listen()
        msg = s.recv(1024)
        msg.decode()

        if not msg[0]:
            print(msg[1])
            sys.exit(2)

        # print rec_msg[1] to command line
        print(msg[1])

        # receive message from Server
            # validate
            # decrypt message

        while True:
            command = input("secure drop> ").lower()
            if command == "exit":
                print("Goodbye.")
                exit(1)
            if command in ACTION_LIST:
                match command:
                    case "help":
                        msg = '\t"add" -> Add a new contact'
                        msg.append('\n\t"list" -> List all online contacts')
                        msg.append('\n\t"send" -> Transfer file to contact')
                        msg.append('\n\t"exit" -> Exit SecureDrop')
                        print(msg)
                    case "add":
                        full_name, email = f.get_name_and_email()
                        s.send(bytes([True, "add", [email, full_name]]))
                    case "list": # TODO: flesh out
                        s.send(bytes([True, "list", []]))
                    case "send": # TODO: flesh out
                        pass
            else:
                print("Command Not Recognized.")
                print('Type "help" For Commands')


#########
# Start #
#########
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

rec_msg = str()
msg = str()

s.connect((host, port))
# connect to Server

# s.listen()
# rec_msg = s.recv(1024)
# rec_msg.decode()
# print(rec_msg)

msg = login_loop()

s.send(bytes(msg))

main_loop()

s.close()
