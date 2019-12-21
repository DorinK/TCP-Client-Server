import socket
import sys

BUFFER_SIZE = 1024


# Saving the info of the client in mode 0 -listening port and files- in the server.
def connect_listening_client():

    listen_port = user_input[1]
    files_str = user_input[2]

    # Splitting the files string using comma.
    files_lst = files_str.split(',')

    # Saving in a dictionary the listening port and files list as a tuple.
    users_files[client_address] = (listen_port, files_lst)


# Searching for relevant files in the server - for client in mode 1.
def search():

    # If the user didn't mention the file name.
    if len(user_input) == 1:
        client_socket.send('\n'.encode())

    else:  # Otherwise.
        search_obj = user_input[1]
        search_result = ""

        # Searching for a match.
        for client_info, (listen_port, files) in zip(users_files.keys(), users_files.values()):
            files_names = [i for i in files if search_obj in i]
            for file_name in files_names:
                search_result += ("," + file_name + " " + client_info[0] + " " + listen_port)

        # Removing the first comma from the string.
        response = search_result[1:]

        # Adding the "\n" in order to send the server response.
        response += "\n"

        # Sending the response.
        client_socket.send(response.encode())


# Defining a socket in order to connect to listen to clients.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = '0.0.0.0'

# Receive number of port of the server from command line.
server_port = int(sys.argv[1])
server.bind((server_ip, server_port))
server.listen(5)

# Dictionary where the key is the client_address and the value is a tuple contains the listening port and a list
# of all files.
users_files = {}

while True:

    # Opening a socket to the client.
    client_socket, client_address = server.accept()

    # Receiving the user's request.
    data = client_socket.recv(BUFFER_SIZE)

    # As long as the server hasn't received the entire client's request, it keeps reading.
    while chr(data[len(data) - 1]) != '\n':
        data += client_socket.recv(BUFFER_SIZE)

    # Splitting the data
    user_input = data.decode().split()
    option = user_input[0]

    # If client wants to connect to the server.
    if option == '1':
        connect_listening_client()

    # If the client wants to search in the server.
    elif option == '2':
        search()

    # Close the socket after one request.
    client_socket.close()
