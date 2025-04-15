import sys
import socket
import functions as f
import key_gen as k


ACTION_LIST = ["help", "add", "list", "send", "exit"]


def main():
    # Creates the TCP socket(AF_INET means address family: IPv4/127.0.0.1, and SOCK_STREAM means socket type, TCP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get IP and Port from command line, I used 127.0.0.1 10000 for testing
    if len(sys.argv) != 3: # Checks to see if total number of command line arguments were passed, and if not enough displays error
        print(f"Usage: python {sys.argv[0]} <IP> <PORT>")
        sys.exit(1)

    ip = sys.argv[1] # Creates variable ip which takes the first command line argument and saves it as the ip, in our case (127.0.0.1)
    try:
        port = int(sys.argv[2]) # This try block is used to make sure port is an actually number, if not it exits with error
    except ValueError:
        print("Port must be an integer.")
        sys.exit(1)

    server_address = (ip, port) # Sets server address to the correct IP and Port
    print("Starting up server on %s port %s" % server_address)
    sock.bind(server_address) # Tells the socket to listen on this IP address and port(Reserves the two for listening for events)
    sock.listen(1) # This actually starts the listening event, unlike the above line which initalizes the socket to listen for the IP and Port.

     # initial dictionary, will be used to save client information, including the email and password for future logins
    user_database = {}
    user_database["User"] = {}


    email = ""
    logged_in = False
    while not logged_in:
        print("WAITING FOR CONNECTION")
        connection, client_address = sock.accept() # This waits for a client to acually connect to server

        logged_in, command, data = connection.recv(1024)
        # recieve message in following form:
        # [logged_in:bool, command:str, data:list]
        try:
            print("CONNECTION ESTABLISHED FROM", client_address) # This will print out a message when a client connects to the server (Will show the IP and Port)
            # [logged_in:bool, command:str, data:list]
            logged_in, command, data = connection.recv(1024)

            if command == "login":
                new, user, password = data
                email = user[0]

                success, message = f.login_server(user_database, new, user, password)

                if success:
                    logged_in = True

                connection.send(bytes([False, message]))
            else:
                connection.send(bytes([False, "Please Log In."]))
        finally:
            connection.close()

    while True:
        try:
            print("CONNECTION ESTABLISHED FROM", client_address) # This will print out a message when a client connects to the server (Will show the IP and Port)
            # [logged_in:bool, command:str, data:list]
            logged_in, command, data = connection.recv(1024)

            if command in ACTION_LIST:
                msg = f.actions_server(user_database, command, email, data)
                connection.send(bytes([True, msg]))
            else:
                connection.send(bytes([True, "Invalid Command."]))

        finally:
            connection.close()


#########
# Start #
#########
if __name__ == "__main__":
    # try:
    #     open("private_key.pem", "rb")
    # except FileNotFoundError:
    #     k.gen_keys()

    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting Server Down.")
        sys.exit(0)
