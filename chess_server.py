import socket
import select
import random

HOST = socket.gethostbyname(socket.gethostname())
PORT = 1729

server_socket = socket.socket()
server_socket.bind((HOST, PORT))
server_socket.listen(5)
open_client_sockets = []
messages_to_send = []
clients_dict = {}
BOARD_SIZE = 8



def get_opposite_point(point):
    new_y = (BOARD_SIZE - 1) - point[1]
    new_x = (BOARD_SIZE - 1) - point[0]
    return new_x, new_y


def send_waiting_messages(write_list):
    for message in messages_to_send:
        clients_socket, data = message
        if clients_socket in write_list:
            clients_socket.send(data)
            messages_to_send.remove(message)


def send_message(client_socket, message):
    messages_to_send.append((client_socket, get_length_in_bytes(message) + message))


def get_length_in_bytes(message):
    message_length = str(len(message))
    if len(message_length) < 2:
        message_length = "0" + message_length
    return message_length


def handle_client_request(client_socket):  # move quit checkmate
    try:
        client_request = client_socket.recv(4)
    except socket.error:
        open_client_sockets.remove(client_socket)
        clients_dict.pop(client_socket)
        return

    if client_request == "MOVE":
        old_point_x = int(client_socket.recv(1))
        old_point_y = int(client_socket.recv(1))
        new_point_x = int(client_socket.recv(1))
        new_point_y = int(client_socket.recv(1))
        old_point = (old_point_x, old_point_y)
        new_point = (new_point_x, new_point_y)

        old_point = get_opposite_point(old_point)
        new_point = get_opposite_point(new_point)

        print old_point
        print new_point

        for other_client_socket in open_client_sockets:
            if other_client_socket != client_socket:
                data = "04MOVE" + str(old_point[0]) + str(old_point[1]) + str(new_point[0]) + str(new_point[1])
                messages_to_send.append((other_client_socket, data))

    if client_request == "QUIT":
        for other_client_socket in open_client_sockets:
            if other_client_socket != client_socket:
                send_message(other_client_socket, "QUIT")
        open_client_sockets.remove(client_socket)
        clients_dict.pop(client_socket)

    if client_request == "MATE":
        for other_client_socket in open_client_sockets:
            if other_client_socket != client_socket:
                send_message(other_client_socket, "WIN")
        open_client_sockets.remove(client_socket)
        clients_dict.pop(client_socket)


def start_game():
    rand_num = random.randint(0, 1)
    client_one_color = "white"
    client_two_color = "black"
    if rand_num == 1:
        client_one_color = "black"
        client_two_color = "white"

    clients_dict.update({open_client_sockets[0]: client_one_color})
    clients_dict.update({open_client_sockets[1]: client_two_color})

    for client_socket in open_client_sockets:
        start_bytes_length = get_length_in_bytes("START")
        color_bytes_length = get_length_in_bytes(clients_dict[client_socket])
        data = start_bytes_length + "START" + color_bytes_length + clients_dict[client_socket]
        messages_to_send.append((client_socket, data))


def main():
    print "Hosting server on \nIP: %s \nPORT: %s" % (HOST, PORT)
    print

    while True:
        read_list, write_list, x_list = select.select([server_socket] + open_client_sockets, open_client_sockets, [])
        for current_socket in read_list:
            if current_socket is server_socket:
                new_client_socket, address = server_socket.accept()
                open_client_sockets.append(new_client_socket)
                if len(open_client_sockets) == 2:
                    start_game()
            else:
                if current_socket in open_client_sockets:
                    handle_client_request(current_socket)

        send_waiting_messages(write_list)


if __name__ == '__main__':
    main()
