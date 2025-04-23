import json
import socket
import sys
import threading
import functions as f
import key_gen as k


# TODO: log out client on disconnect or after X amount of time idle

LOGGED_IN = "Logged_In"


def handle_client(connection, client_address, user_database):
    try:
        try:
            logged_in = user_database[LOGGED_IN][client_address] # If client is in the database, check if logged in
        except KeyError:
            user_database[LOGGED_IN][client_address] = False # If client has never logged in, set their status to false

            logged_in = user_database[LOGGED_IN][client_address] # Refresh the login

        msg_in = connection.recv(1024).decode()
        command, data, username = json.loads(msg_in)
        # recieve message in following form:
        # [command:str, data:list, username:str]

        print("command in:", command) # TODO: Delete

        if command == "ping":
            print("ping if!") # TODO: Delete
            if not logged_in:
                connection.send(bytes(json.dumps([True, f.LOGIN_COM]), "utf-8"))
            else:
                connection.send(bytes(json.dumps([True, "ping back"]), "utf-8"))
            print("Pre-close") # TODO: Delete
            connection.close()
            print("Post-close") # TODO: Delete
            return

        if not logged_in:
            print("CONNECTION ESTABLISHED FROM", client_address) # This will print out a message when a client connects to the server (Will show the IP and Port)

            if command == "login":
                new, user, password = data
                success, message = f.login_server(user_database, new, user, password)

                logged_in = success

                connection.send(bytes(json.dumps([success, message]), "utf-8"))
            else:
                connection.send(bytes(json.dumps([False, "Please Log In."]), "utf-8"))
            connection.close()
            return

        print("CONNECTION ESTABLISHED FROM", client_address) # This will print out a message when a client connects to the server (Will show the IP and Port)

        if command in f.ACTION_LIST:
            msg = f.actions_server(user_database, command, username, data)
            connection.send(bytes(json.dumps([True, msg]), "utf-8"))
        else:
            connection.send(bytes(json.dumps([True, "Invalid Command."]), "utf-8"))

        connection.close()
        return

    except Exception as e:
        print(f"[!] Error with {client_address}: {e}")
        connection.close()


def main():
    # Creates the TCP socket(AF_INET means address family: IPv4/127.0.0.1, and SOCK_STREAM means socket type, TCP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get IP and Port from command line, I used 127.0.0.1 10000 for testing
    if len(sys.argv) != 3: # Checks to see if total number of command line arguments were passed, and if not enough displays error
        print(f"Usage: python3 {sys.argv[0]} <IP> <PORT>")
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
    sock.listen(20) # This actually starts the listening event, unlike the above line which initalizes the socket to listen for the IP and Port.

     # initial dictionary, will be used to save client information, including the email and password for future logins
    user_database = {}
    user_database[f.USER] = {}
    user_database[LOGGED_IN] = {}

    while True:
        print("WAITING FOR CONNECTION")
        connection, client_address = sock.accept() # This waits for a client to acually connect to server
        print(connection) # Used for testing, connection is initialized as the socket
        print(client_address) # Used for testing, client_address is initialized as the ip address and port
        # Creates a thread that will handle clients one at a time rather than all at once(1 thread for each new user connecting to server)
        client_thread = threading.Thread(
            target=handle_client, # calls and passes in a few argumanets to handle client
            args=(connection, client_address, user_database) # Our connection(socket), our client_address(ip and port), and our user database
        )
        print("Pre-thread start") # TODO: Delete
        client_thread.start() # Starts the thread
        print("Post-thread start") # TODO: Delete


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
