import sys
import socket

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

    while True:
        print("WAITING FOR CONNECTION")
        connection, client_address = sock.accept() # This waits for a client to acually connect to server

        try:
            print("CONNECTION ESTABLISHED FROM", client_address) # This will print out a message when a client connects to the server(Will show the IP and Port)
            
        finally:
            connection.close()

# launch server (done)

# move database to server (not done)


#########
# Start #
#########
if __name__ == "__main__":
    main()
    # server spin up
        # pull ip and port from "sys.argv[1]" and "sys.agrv[2]"
    # create empty database
    # while True:
        # try:
            # listen for message
            # receive message from a recipient
                # validate message
                # decode message
                # if message is approved command - execute
            # create rec_msg[bool, string]
                # encode message
            # send message back to same recipient
        # catch KeyInterrupt:
            # exit(0)
    pass
