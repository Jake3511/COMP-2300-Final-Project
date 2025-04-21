import json
import socket
import sys
import functions as f


# TODO: log out client on disconnect or after X amount of time idle

LOGGED_IN = "Logged_In"


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
    user_database[f.USER] = {}
    user_database[LOGGED_IN] = {}

    email = ""
    while True:
        print("WAITING FOR CONNECTION")
        connection, client_address = sock.accept() # This waits for a client to acually connect to server

        msg_in = connection.recv(1024).decode()
        command, data = json.loads(msg_in)
        # recieve message in following form:
        # [command:str, data:list]

        print("CONNECTION ESTABLISHED FROM", client_address) # This will print out a message when a client connects to the server (Will show the IP and Port)

        try:
            logged_in = user_database[LOGGED_IN][client_address]
        except KeyError:
            user_database[LOGGED_IN][client_address] = False
            logged_in = user_database[LOGGED_IN][client_address]

        if not logged_in:
            connection.send(bytes(json.dumps([True, f.LOGIN_COM]), "utf-8"))

            connection.close()
            connection, client_address = sock.accept()

            msg_in = connection.recv(1024).decode("utf-8")
            command, data = json.loads(msg_in)

            if command == f.LOGIN_COM:
                new, user, password = data
                email = user[0]

                success, message = f.login_server(user_database, new, user, password)

                if success:
                    user_database[LOGGED_IN][client_address] = True
                    logged_in = user_database[LOGGED_IN][client_address]

                connection.send(bytes(json.dumps([success, message]), "utf-8"))
            else:
                connection.send(bytes(json.dumps([False, "Please Log In."]), "utf-8"))
            connection.close()
            continue

        if command in f.ACTION_LIST:
            msg = f.actions_server(user_database, command, email, data)
            connection.send(bytes(json.dumps([True, msg]), "utf-8"))
        elif command == "ping":
            connection.send(bytes(json.dumps([True, "ping back"]), "utf-8"))
        else:
            connection.send(bytes(json.dumps([True, "Invalid Command."]), "utf-8"))

        connection.close()


#########
# Start #
#########
if __name__ == "__main__":
    try:
        open("./Salt.bin", "rb")
    except FileNotFoundError:
        salt = f.SALT
        with open("./Salt.bin", "wb") as salt_file:
            salt_file.write(salt)

    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting Server Down.")
        sys.exit(0)
