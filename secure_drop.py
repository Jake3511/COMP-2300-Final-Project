import sys
import socket
import functions as f
import fcrypt

#########
# Start #
#########
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#family, type
#he SOCK_STREAM means connection-oriented TCP protocol.
print("Socket connection: success")
host = sys.argv[1] #local host
port = int(sys.argv[2]) #port number
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
print("client has been assigned socket name: ", s.getsockname())

rec_msg = str()
msg = str()

s.connect((host, port))
# connect to Server

success, ret_user, email, full_name, password = f.login_client()
if not success:
    print("Login Failed; Goodbye.")
    sys.exit(1)
else:
    s.listen()
    rec_msg = s.recv(port)
    rec_msg.decode()
    send_msg = [False, "login", [ret_user, [email, full_name], password]]
    s.send(bytes(send_msg, "utf-8"))

while True:
    # msg = s.recv(1024)
    s.listen()
    msg = s.recv(port)
    msg.decode()


    if msg[0] == False:
        print("Goodbye")
        sys.exit(2)

    # print rec_msg[1] to command line
    print(msg[1])

    # receive message from Server
        # validate
        # decrypt message

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
