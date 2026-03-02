import Tkinter as tk
from PIL import ImageTk, Image
import socket
import select
import threading

PORT = 1729
IP = 'NONE'
ADDRESS = (IP, PORT)
client_socket = socket.socket()
messages_to_send = []

root = tk.Tk()
root.attributes("-fullscreen", True)
root.title('Chess')

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
screen_size = (screen_width, screen_height)

WHITE = "white"
BLACK = "black"
connected = threading.Event()
TWO = 2
ONE = 1
ZERO = 0
PIXEL_SIZE = 1
BOARD_SIZE = 8
chess_board_dict = {}
BISHOP = "bishop"
KNIGHT = "knight"
ROOK = "rook"
PAWN = "pawn"
QUEEN = "queen"
KING = "king"
is_selected = False
selected_point = None
GAME_SQUARE_SIZE = screen_width / 20
EMPTY_PIXEL = tk.PhotoImage(width=PIXEL_SIZE, height=PIXEL_SIZE)
SIX = 6
show_possible_moves = True
RED = 'red'
GREEN = 'green'

game_info_label = tk.Label()
is_player_turn = False

player_color = ""
other_player_color = ""


def rgb_to_tkinter_color(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb


BROWN = rgb_to_tkinter_color((181, 154, 132))


def get_render(game_object, color):
    file_name = "images/chess_%s_%s.png" % (color, game_object)
    return ImageTk.PhotoImage(Image.open(file_name))


class GameObject:
    def __init__(self, widget, game_object=None, color=None, render=None):
        self.widget = widget
        self.render = render
        self.game_object = game_object
        self.color = color

    def is_empty(self):
        if self.game_object is None:
            return True
        return False


class BackgroundImage:
    def __init__(self, file_name):
        self.render = Image.open(file_name)
        self.render = self.render.resize(screen_size, Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(self.render)
        self.tk_label = tk.Label(root, image=self.image)

    def set(self, file_name):
        self.render = Image.open(file_name)
        self.render = self.render.resize(screen_size, Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(self.render)
        self.tk_label = tk.Label(root, image=self.image)


background_image = BackgroundImage("images/menu_background.jpg")


def place(point, game_object, color):
    render = get_render(game_object, color)
    chess_board_dict[point].render = render
    chess_board_dict[point].color = color
    chess_board_dict[point].game_object = game_object
    chess_board_dict[point].widget.config(image=render, width=GAME_SQUARE_SIZE, height=GAME_SQUARE_SIZE)


def is_valid_point(point):
    x = point[ZERO]
    y = point[ONE]
    if x < ZERO or x >= BOARD_SIZE:
        return False
    if y < ZERO or y >= BOARD_SIZE:
        return False

    return True


def get_pawn_moves(point, is_scanning_king_danger):
    x = point[ZERO]
    y = point[ONE]
    moves_list = []

    object_color = chess_board_dict[point].color
    other_object_color = BLACK
    if object_color == BLACK:
        other_object_color = WHITE

    if not is_scanning_king_danger:
        new_point = (x, y - 1)
        if is_valid_point(new_point) and chess_board_dict[new_point].is_empty() and object_color == player_color:
            moves_list.append(new_point)

        if y == SIX and chess_board_dict[new_point].is_empty() and object_color == player_color:
            new_point = (x, y - 2)
            if is_valid_point(new_point) and chess_board_dict[new_point].is_empty():
                moves_list.append(new_point)

        new_point = (x - 1, y - 1)
        if is_valid_point(new_point) and chess_board_dict[new_point].color == other_object_color:
            moves_list.append(new_point)
        new_point = (x + 1, y - 1)
        if is_valid_point(new_point) and chess_board_dict[new_point].color == other_object_color:
            moves_list.append(new_point)
    else:  # only the eat moves to check if king is in danger
        new_point = (x - 1, y + 1)
        if is_valid_point(new_point):
            moves_list.append(new_point)
        new_point = (x + 1, y + 1)
        if is_valid_point(new_point):
            moves_list.append(new_point)

    return moves_list


def get_knight_moves(point):
    x = point[ZERO]
    y = point[ONE]
    moves_list = []

    object_color = chess_board_dict[point].color

    new_point = (x - 2, y - 1)
    if is_valid_point(new_point) and chess_board_dict[new_point].color != object_color:
        moves_list.append(new_point)
    new_point = (x + 2, y - 1)
    if is_valid_point(new_point) and chess_board_dict[new_point].color != object_color:
        moves_list.append(new_point)
    new_point = (x - 2, y + 1)
    if is_valid_point(new_point) and chess_board_dict[new_point].color != object_color:
        moves_list.append(new_point)
    new_point = (x + 2, y + 1)
    if is_valid_point(new_point) and chess_board_dict[new_point].color != object_color:
        moves_list.append(new_point)

    new_point = (x - 1, y - 2)
    if is_valid_point(new_point) and chess_board_dict[new_point].color != object_color:
        moves_list.append(new_point)
    new_point = (x + 1, y - 2)
    if is_valid_point(new_point) and chess_board_dict[new_point].color != object_color:
        moves_list.append(new_point)
    new_point = (x - 1, y + 2)
    if is_valid_point(new_point) and chess_board_dict[new_point].color != object_color:
        moves_list.append(new_point)
    new_point = (x + 1, y + 2)
    if is_valid_point(new_point) and chess_board_dict[new_point].color != object_color:
        moves_list.append(new_point)

    return moves_list


def get_rook_moves(point):
    x = point[ZERO]
    y = point[ONE]
    moves_list = []

    object_color = chess_board_dict[point].color

    for i in range(x + 1, BOARD_SIZE):
        new_point = (i, y)
        if chess_board_dict[new_point].color != object_color:
            moves_list.append(new_point)

        if not chess_board_dict[new_point].is_empty():
            break

    i = x - 1
    while i >= 0:
        new_point = (i, y)
        if chess_board_dict[new_point].color != object_color:
            moves_list.append(new_point)

        if not chess_board_dict[new_point].is_empty():
            break
        i -= 1

    for i in range(y + 1, BOARD_SIZE):
        new_point = (x, i)
        if chess_board_dict[new_point].color != object_color:
            moves_list.append(new_point)

        if not chess_board_dict[new_point].is_empty():
            break

    i = y - 1
    while i >= 0:
        new_point = (x, i)
        if chess_board_dict[new_point].color != object_color:
            moves_list.append(new_point)

        if not chess_board_dict[new_point].is_empty():
            break
        i -= 1

    return moves_list


def get_bishop_moves(point):
    x = point[ZERO]
    y = point[ONE]
    moves_list = []

    object_color = chess_board_dict[point].color

    for i in range(1, BOARD_SIZE):
        new_point = (x - i, y - i)
        if is_valid_point(new_point):
            if chess_board_dict[new_point].color != object_color:
                moves_list.append(new_point)
        else:
            break

        if not chess_board_dict[new_point].is_empty():
            break

    for i in range(1, BOARD_SIZE):
        new_point = (x + i, y + i)
        if is_valid_point(new_point):
            if chess_board_dict[new_point].color != object_color:
                moves_list.append(new_point)
        else:
            break

        if not chess_board_dict[new_point].is_empty():
            break

    for i in range(1, BOARD_SIZE):
        new_point = (x + i, y - i)
        if is_valid_point(new_point):
            if chess_board_dict[new_point].color != object_color:
                moves_list.append(new_point)
        else:
            break

        if not chess_board_dict[new_point].is_empty():
            break

    for i in range(1, BOARD_SIZE):
        new_point = (x - i, y + i)
        if is_valid_point(new_point):
            if chess_board_dict[new_point].color != object_color:
                moves_list.append(new_point)
        else:
            break

        if not chess_board_dict[new_point].is_empty():
            break

    return moves_list


def get_queen_moves(point):
    return get_rook_moves(point) + get_bishop_moves(point)


def get_king_moves(point):
    x = point[ZERO]
    y = point[ONE]
    moves_list = []

    object_color = chess_board_dict[point].color

    for i in range(y - 1, y + 2):
        for j in range(x - 1, x + 2):
            new_point = (j, i)
            if is_valid_point(new_point):
                if chess_board_dict[new_point].color != object_color:
                    moves_list.append(new_point)

    return moves_list


def get_possible_moves_list(point, is_scanning_king_danger=False):
    game_object = chess_board_dict[point].game_object
    moves_list = []

    if game_object is PAWN:
        moves_list = get_pawn_moves(point, is_scanning_king_danger)

    if game_object is KNIGHT:
        moves_list = get_knight_moves(point)

    if game_object is ROOK:
        moves_list = get_rook_moves(point)

    if game_object is BISHOP:
        moves_list = get_bishop_moves(point)

    if game_object is QUEEN:
        moves_list = get_queen_moves(point)

    if game_object is KING:
        moves_list = get_king_moves(point)

    if not is_scanning_king_danger:
        new_moves_list = []
        for new_point in moves_list:
            if not will_king_be_in_danger(new_point, point):
                new_moves_list.append(new_point)

        return new_moves_list
    return moves_list


def move(point, new_point):
    render = chess_board_dict[point].render

    chess_board_dict[new_point].render = render
    chess_board_dict[new_point].color = chess_board_dict[point].color
    chess_board_dict[new_point].game_object = chess_board_dict[point].game_object
    chess_board_dict[new_point].widget.config(image=render, width=GAME_SQUARE_SIZE, height=GAME_SQUARE_SIZE)

    chess_board_dict[point].render = None
    chess_board_dict[point].color = None
    chess_board_dict[point].game_object = None
    chess_board_dict[point].widget.config(image=EMPTY_PIXEL, width=GAME_SQUARE_SIZE, height=GAME_SQUARE_SIZE)


def clear_board_colors():
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if y % TWO == ZERO:
                if x % TWO == ZERO:
                    color = WHITE
                else:
                    color = BROWN
            else:
                if x % TWO == ZERO:
                    color = BROWN
                else:
                    color = WHITE

            chess_board_dict[(x, y)].widget['bg'] = color


def show_possible_moves_function(widget):
    global show_possible_moves

    if show_possible_moves:
        widget['bg'] = RED
        widget['text'] = 'Show Possible Moves: OFF'
        clear_board_colors()
        show_possible_moves = False
    else:
        widget['bg'] = GREEN
        widget['text'] = 'Show Possible Moves: ON'
        if selected_point:
            for my_point in get_possible_moves_list(selected_point):
                chess_board_dict[my_point].widget['bg'] = RED
        show_possible_moves = True


def get_player_king_point():
    king_point = None
    for point in chess_board_dict:
        if chess_board_dict[point].game_object is KING and chess_board_dict[point].color == player_color:
            king_point = point
            break

    return king_point


def will_king_be_in_danger(new_point, current_object_point):
    is_danger = False

    temp_color = chess_board_dict[new_point].color
    temp_object = chess_board_dict[new_point].game_object

    chess_board_dict[new_point].color = chess_board_dict[current_object_point].color
    chess_board_dict[new_point].game_object = chess_board_dict[current_object_point].game_object

    chess_board_dict[current_object_point].color = None
    chess_board_dict[current_object_point].game_object = None

    king_point = get_player_king_point()

    for point in chess_board_dict:
        if king_point in get_possible_moves_list(point, is_scanning_king_danger=True):
            if chess_board_dict[point].color != player_color:
                is_danger = True

    chess_board_dict[current_object_point].color = chess_board_dict[new_point].color
    chess_board_dict[current_object_point].game_object = chess_board_dict[new_point].game_object
    chess_board_dict[new_point].color = temp_color
    chess_board_dict[new_point].game_object = temp_object
    return is_danger


def is_check_mate():
    all_possible_player_moves = []

    for point in chess_board_dict:
        if chess_board_dict[point].color == player_color:
            all_possible_player_moves += get_possible_moves_list(point)

    return len(all_possible_player_moves) == ZERO


def create_board():
    global game_info_label
    global chess_board_dict
    clear_screen()
    chess_board_dict = {}

    background_image.set("images/background.jpg")
    background_image.tk_label.place(x=0, y=0, relwidth=1, relheight=1)

    board_canvas = tk.Canvas(root)
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            point = (col, row)
            board_button = tk.Button(board_canvas, image=EMPTY_PIXEL, width=GAME_SQUARE_SIZE, height=GAME_SQUARE_SIZE)
            board_button.config(command=lambda arg=point: select_game_square(arg))
            board_button.grid(row=row, column=col)
            chess_board_dict.update({point: GameObject(board_button)})

    clear_board_colors()

    for x in range(BOARD_SIZE):
        place((x, 1), PAWN, other_player_color)
        place((x, 6), PAWN, player_color)

    place((0, 0), ROOK, other_player_color)
    place((1, 0), BISHOP, other_player_color)
    place((2, 0), KNIGHT, other_player_color)

    if other_player_color == BLACK:
        place((3, 0), QUEEN, other_player_color)
        place((4, 0), KING, other_player_color)
    else:
        place((3, 0), KING, other_player_color)
        place((4, 0), QUEEN, other_player_color)

    place((5, 0), KNIGHT, other_player_color)
    place((6, 0), BISHOP, other_player_color)
    place((7, 0), ROOK, other_player_color)

    place((0, 7), ROOK, player_color)
    place((1, 7), BISHOP, player_color)
    place((2, 7), KNIGHT, player_color)

    if player_color == WHITE:
        place((3, 7), QUEEN, player_color)
        place((4, 7), KING, player_color)
    else:
        place((3, 7), KING, player_color)
        place((4, 7), QUEEN, player_color)

    place((5, 7), KNIGHT, player_color)
    place((6, 7), BISHOP, player_color)
    place((7, 7), ROOK, player_color)

    quit_button = tk.Button(bg='white', text='Quit', command=quit_game, width=10)
    quit_button.pack()

    show_moves_button = tk.Button(text='Show Possible Moves: ON', bg=GREEN)
    show_moves_button.config(command=lambda: show_possible_moves_function(show_moves_button))
    show_moves_button.pack()

    board_canvas.pack()
    tk.Frame(bg=player_color, width=50, height=50).pack()
    label_text = "Other player's turn"
    if is_player_turn:
        label_text = "Your turn"
    game_info_label = tk.Label(root, font=("Arial 18", 14), text=label_text)
    game_info_label.pack()


def quit_game():
    if connected.is_set():
        messages_to_send.append("QUIT")
    main()


def select_game_square(point):
    global is_selected
    global selected_point
    global is_player_turn

    if is_player_turn:
        did_player_move = False
        if is_selected:
            if point in get_possible_moves_list(selected_point):
                did_player_move = True
                game_info_label['text'] = "Other player's turn"
                move(selected_point, point)
                data = "MOVE" + str(selected_point[0]) + str(selected_point[1]) + str(point[0]) + str(point[1])
                messages_to_send.append(data)
                clear_board_colors()
                chess_board_dict[selected_point].widget['relief'] = 'raised'
                is_player_turn = False
                is_selected = False
                selected_point = None

        if chess_board_dict[point].color == player_color and not did_player_move:
            if is_selected:
                clear_board_colors()
                chess_board_dict[selected_point].widget['relief'] = 'raised'

            is_selected = True
            selected_point = point
            chess_board_dict[point].widget['relief'] = 'sunken'
            if show_possible_moves:
                for my_point in get_possible_moves_list(selected_point):
                    chess_board_dict[my_point].widget['bg'] = RED


def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()


def queue_join_game():
    global client_socket
    clear_screen()
    background_image.set("images/menu_background.jpg")
    background_image.tk_label.place(x=0, y=0, relwidth=1, relheight=1)
    tk.Label(font=("Arial 18", 32), text="Waiting for another player to join...").pack()

    client_socket = socket.socket()
    connected.set()
    client_socket.connect(ADDRESS)
    root.after(1, run_client)


def run_client():
    global player_color
    global other_player_color
    global is_player_turn

    read_list, write_list, x_list = select.select([client_socket], [client_socket], [])
    for message in messages_to_send:
        print message
        if client_socket in write_list:
            if message == "QUIT" or message == "MATE":
                connected.clear()
            client_socket.send(message)
            messages_to_send.remove(message)

    if client_socket in read_list:
        data_size = int(client_socket.recv(2))
        action = client_socket.recv(data_size)
        print action
        if action == "START":
            data_size = int(client_socket.recv(2))
            player_color = client_socket.recv(data_size)
            print player_color
            if player_color == WHITE:
                is_player_turn = True

            other_player_color = BLACK
            if other_player_color == player_color:
                other_player_color = WHITE
            create_board()
        if action == "MOVE":
            old_point_x = int(client_socket.recv(1))
            old_point_y = int(client_socket.recv(1))
            new_point_x = int(client_socket.recv(1))
            new_point_y = int(client_socket.recv(1))
            old_point = (old_point_x, old_point_y)
            new_point = (new_point_x, new_point_y)
            move(old_point, new_point)
            if not is_check_mate():
                is_player_turn = True
                game_info_label['text'] = 'Your turn'
            else:
                game_info_label['text'] = 'Check mate! You lost!'
                messages_to_send.append("MATE")
        if action == "WIN":
            messages_to_send.append("QUIT")
            game_info_label['text'] = 'Check mate! You win!'
        if action == "QUIT":
            is_player_turn = False
            messages_to_send.append("QUIT")
            game_info_label['text'] = 'Other player left! You win!'

    if connected.is_set():
        root.after(1, run_client)
    else:
        client_socket.close()


def main():
    global is_player_turn
    global selected_point
    global is_selected
    global show_possible_moves
    show_possible_moves = True
    is_selected = False
    selected_point = None
    is_player_turn = False
    clear_screen()
    background_image.set("images/menu_background.jpg")
    background_image.tk_label.place(x=0, y=0, relwidth=1, relheight=1)
    join_game_button = tk.Button(font=("Arial 18", 32), bg='white', text='Join Game', width=10)
    join_game_button.config(command=queue_join_game)
    join_game_button.pack()
    quit_button = tk.Button(font=("Arial 18", 32), bg='white', text='Quit', command=root.quit, width=10)
    quit_button.pack()


if __name__ == '__main__':
    main()
    root.mainloop()
