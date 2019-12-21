import socket
import sys
import os

BUFFER_SIZE = 1024

# Receive arguments of client mode and IP + port of the server from command line.
mode = str(sys.argv[1])
server_ip = str(sys.argv[2])
server_port = int(sys.argv[3])


# Function in which client in listening mode connects to the server.
def connect_to_server():

    # Getting the full path of the current directory.
    cwd = os.getcwd()

    files_lst = []
    # Searching in the current directory for files.
    for item in os.listdir(cwd):
        temp = os.path.join(cwd, item)
        # Listing all the files in the current directory.
        if os.path.isfile(temp):
            if item != '.DS_Store':
                files_lst.append(item)

    # Defining a socket in order to connect to the server.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))

    # Creating a string which contains all the files found in the current directory.
    files_str = ','.join([str(elem) for elem in files_lst])

    # Composing the request to the server.
    msg = "1 " + str(listening_port) + " " + files_str + "\n"

    # Sending the request.
    s.send(msg.encode())

    # Close the socket.
    s.close()


# Function in which the client is now listens and waits for clients file's requests.
def listen_to_clients():

    # Defining a socket in order to listen to clients.
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Binding to the listening port
    listening_socket.bind(('127.0.0.1', listening_port))
    listening_socket.listen(1)

    while True:
        # Opening a socket to a client.
        client_socket, client_address = listening_socket.accept()

        # Receiving the requested file name.
        file_details = client_socket.recv(BUFFER_SIZE).decode()

        # As long as the client in listening mode hasn't received the entire file's name, it keeps reading.
        while file_details[len(file_details) - 1] != '\n':
            file_details += client_socket.recv(BUFFER_SIZE).decode()

        # Pulling out the file name from the string.
        file_details = file_details.split('\n')[0]

        # Opening the requested file as a binary file.
        with open(file_details, "rb") as file:

            # Reading the file's content.
            data = file.read()

            # Sending the file's content to the client which requested it.
            client_socket.send(data)

        # Close the socket.
        client_socket.close()


# Function in which client in user mode asks the server to search in it's files for a match.
def search_in_server():

    # Defining a socket in order to connect to the server.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, server_port))

    # Composing the request to the server.
    msg = "2 " + to_search + "\n"

    # Sending the request.
    s.send(msg.encode())

    # Getting the server's response.
    server_response = s.recv(BUFFER_SIZE)

    # As long as the client in user mode hasn't received the entire server response, it keeps reading.
    while chr(server_response[len(server_response) - 1]) != '\n':
        server_response += s.recv(BUFFER_SIZE)

    # Close the socket.
    s.close()

    return server_response


# Processing the server response into a list of files which found as a match.
def process_server_response():

    # Splitting by comma.
    files = response.decode().split(',')

    # Creating a list of tuples when each tuple is a file and contact client info.
    files = [tuple(file_info.split()) for file_info in files]

    # Sorting the list alphabetically.
    files = sorted(files, key=lambda file_info: file_info[0])

    # Printing the matching files to the terminal.
    for index, file_details in enumerate(files, 1):
        print("{0} {1}".format(index, file_details[0]))

    return files


# Function in which a client in user mode connects to the relevant client in order to download the requested file.
def download_file(file):

    # Defining a socket in order to connect to the client that has the requested file.
    receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = file[1]
    port = int(file[2])
    receive_socket.connect((ip, port))

    # Sending the file's name.
    receive_socket.send((file[0] + '\n').encode())

    # Opening a new file in the current directory.
    with open("./" + file[0], "wb") as new_file:

        # Receiving the file's content (all of it or part of it if too big).
        data = receive_socket.recv(BUFFER_SIZE)

        # As long as the data is not empty.
        while data:

            # Write into the new file the data we read from the socket.
            new_file.write(data[:len(data)])

            # Keep reading from the socket.
            data = receive_socket.recv(BUFFER_SIZE)

    # Close the socket.
    receive_socket.close()


# If client is in user mode (=0).
if mode == '0':

    # Get the forth argument of the listening port.
    listening_port = int(sys.argv[4])

    # Do the following.
    connect_to_server()
    listen_to_clients()

# If client is in listening mode.
elif mode == '1':

    # Infinite loop.
    while True:

        # Ask the user for what he is searching.
        to_search = input("Search: ")

        # Searching within the server and getting it's response.
        response = search_in_server()

        # If no match was found.
        if response.decode() == '\n':
            to_choose = input("Choose: ")
            continue

        # processing the server's response.
        relevant_files = process_server_response()

        # Asking the user what file he wants to download.
        to_choose = input("Choose: ")

        # If the user's choice is out of format.
        if any(not ch.isdigit() for ch in to_choose) or to_choose == '' or int(to_choose) > len(relevant_files) or int(
                to_choose) == 0:
            continue

        # Finding the requested file.
        wanted_file = relevant_files[int(to_choose) - 1]

        # Opening a connection in order to download the requested file.
        download_file(wanted_file)
