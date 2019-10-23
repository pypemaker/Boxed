import tkinter as tk
from itertools import cycle
from time import sleep
import concurrent.futures
import threading
import socket


class Player:
    """Initiating a player instance with unique values"""

    # Players 1 & 2 constant match colours.
    P_COLOURS = ['#FF3B3F', '#17E4FF']

    """
    Using itertools.cycle() to create an infinite generator to switch 
    between True and False status when calling player_switcher method.
    Thus determining which of the players turn it currently is.
    """
    flipper = cycle([False, True])

    # Storing player object details for future reference.
    players = []


    def __init__(self, name, score, colour, status):
        """Initiating a Player object"""
        self.name = name
        self.score = score
        self.colour = colour
        self.status = status
        self.name_label = MyLabel(window, self.name, BGCOLOUR, self.colour, FONT)
        self.score_label = MyLabel(window, self.score, BGCOLOUR, self.colour, FONT)


    @classmethod
    def player_switcher(cls):
        """Flips player status when called / updates frame label content"""
        for p in cls.players:
            p.status = cls.flipper.__next__()
        cls.flipper.__next__() # offset for next iteration.
        main_frame.configure(text = f"  {cls.current_player().name}'s Turn  ")


    def add_score(self, score):
        """Increments the score value / updates score label"""
        self.score += score
        self.score_label.configure(text = self.score)


    @staticmethod
    def current_player():
        """Returns the current player (self.status == True)"""
        for p in Player.players:
            if p.status == True:
                return p


class MyButton(tk.Button):
    """Configures a button object"""
    def __init__(self, frame, padx, border, bg, cursor, state, name):
        super().__init__(frame)
        self['padx'] = padx
        self['command'] = self.main_controller
        self['border'] = border
        self['bg'] = bg
        self['cursor'] = cursor
        self['state'] = state
        self.name = name


    def main_controller(self, from_send = False):
        """General match flow-control"""

        # Filters client button click if not from the server / not in turn.
        if Player.current_player().name != WINDOW_TITLE and not from_send:
            return

        btn_name = self.name
        
        # Further data verification before transmission.
        if btn_name != last_send and btn_name != last_recv:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                send_thread = executor.submit(Connectivity.send_data, btn_name)

            # Configure / redraw played button.
            self.configure(
                state = 'disabled', bg = DISABLED_COLOUR, 
                relief = 'solid', border = 1, cursor = 'cross'
                )

            # Game logic (see functions for details).
            crc = MyButton.gen_btn_ranges(btn_name)
            Match.game_driver(crc, btn_name, Player.current_player())
            Match.chk_end_game()

        else:
            return


    @staticmethod
    def gen_btn_ranges(num):
        """Generates a range of potential buttons in respect to button clicked"""

        # Returns a dict of grouped button numbers to pass for assessment.
        # Group names are inverted to align with the grid.
        numbers = {
                'down': [num - (RANGE * 2), num - RANGE - 1, num - RANGE + 1],
                'up': [num + (RANGE * 2), num + RANGE + 1, num + RANGE - 1],
                'left': [num + 2, num - RANGE + 1, num + RANGE + 1],
                'right': [ num - 2, num - RANGE - 1, num + RANGE - 1]
            }
        return numbers


    @staticmethod
    def make_button():
        """Generates a button object"""
        b = MyButton(main_frame, PADDING, 1, BUTTON_COLOUR, 'dotbox', 'normal', c)
        b.grid(row = i, column = j)
        buttons_dict[c] = b


    @staticmethod
    def make_square():
        """Generates a square object"""
        s = MyButton(main_frame, PADDING, 0, BGCOLOUR, 'cross', 'disabled', c)
        s.grid(row = i, column = j)
        square_dict[c] = s


class Match(tk.Tk):
    """Generates the main (client) window"""
    def __init__(self, bg, resize_x, resize_y, geometry, title):
        super().__init__()
        self['bg'] = bg
        self.resizable(resize_x, resize_y)
        self.geometry(geometry)
        self.title(title)


    @staticmethod
    def game_driver(btn_list, num, c_player):
        """Calculate and apply score, switch players, redraw tiles"""
        
        score = 0

        """
        Loops over the (down, up, left, right) generated numbers and checks
        for disabled buttons (pressed buttons) in each group. If all set of
        buttons in a specific group are disabled that means that the given 
        pressed button has completed a box around a square, and the score is
        incremented for every such occurrence. The specific square is calculated
        and redrawn with the current player's colour. Supports multiple occurrences.
        """
        for group in btn_list.keys():
            try:
                if all(buttons_dict[g]['state'] == 'disabled' for g in btn_list.get(group)):
                    gain = (sum(btn_list.get(group)) + num) // 4
                    square_dict[gain].configure(
                        bg = c_player.colour, relief='groove', border=1
                        )
                    score += 1

            except KeyError:
                    continue
        if score > 0:
            Player.add_score(c_player, score)
        else:
            Player.player_switcher()


    @staticmethod
    def window_setup():
        """Determines which player every client is as received from the server"""
        while True:
            try:
                data = SOCK.recv(3).decode()
                if 'NO' == data[:2]:
                    global WINDOW_TITLE
                    WINDOW_TITLE = f'Player {data[-1]}'
                    window.title(WINDOW_TITLE)
                    break
            except Exception:
                sleep(0.25)
        return


    @staticmethod
    def chk_end_game():
        """Determines whether the match has ended"""

        """
        Checks if any of the buttons are in 'normal' state, meaning the match
        is still underway. If so break out of the loop and return, else 
        pass the scores to game_over() method.
        """
        if any(buttons_dict[d]['state'] == 'normal' for d in buttons_dict.keys()):
            return
        else:
            Match.game_over((Player.players[0].score, Player.players[1].score))


    @staticmethod
    def game_over(winner):
        """Declare winner and popup window"""
        go_window = Match(BGCOLOUR, False, False, '250x110', 'Game Over')

        p1s, p2s = winner
        if p1s > p2s:
            result = 'Player 1 Wins!'
        elif p1s < p2s:
            result = 'Player 2 Wins!'
        else:
            result = "It's a DRAW!"

        label = tk.Label(
            go_window, text = result, font = FONT, bg = BGCOLOUR, fg = FGCOLOUR
            )
        label.pack(side = 'top', fill = 'x', padx = 15, pady = 15)
        ok = tk.Button(
            go_window, text = 'OK', padx = 15, command = go_window.destroy, 
            font = FONT, bg= BGCOLOUR, fg = FGCOLOUR)
        ok.pack(pady = 5)
        go_window.mainloop()


    @staticmethod
    def switch_theme(theme):
        """Switches between light_theme and dark_mode themes"""

        # Set global variables for future object redraws.
        global BGCOLOUR, BUTTON_COLOUR, DISABLED_COLOUR, FGCOLOUR

        BGCOLOUR = theme.get('BGCOLOUR')
        FGCOLOUR = theme.get('L_FRAME_COLOUR')
        BUTTON_COLOUR = theme.get('BUTTON_COLOUR')
        DISABLED_COLOUR = theme.get('DISABLED_COLOUR')

        def redraw_window():
            """Redraw main window colours"""
            window.configure(bg = BGCOLOUR)
            main_frame.configure(bg = BGCOLOUR, fg = FGCOLOUR)
            theme_button.configure(bg = BGCOLOUR, fg = FGCOLOUR)
            return
        
        def redraw_labels():
            """Redraw label colours"""
            for p in Player.players:
                p.name_label.configure(bg = BGCOLOUR)
                p.score_label.configure(bg = BGCOLOUR)
            return

        def redraw_buttons():
            """Redraw button colours based on state"""
            for b in buttons_dict:
                if buttons_dict[b]['state'] == 'normal':
                    buttons_dict[b].configure(bg = BUTTON_COLOUR)
                else:
                    buttons_dict[b].configure(bg = DISABLED_COLOUR)
            return

        def redraw_squares():
            """Redraw square colours based on state"""
            for s in square_dict:
                if square_dict[s]['bg'] not in Player.P_COLOURS:
                    square_dict[s].configure(bg = BGCOLOUR)
            return

        """
        Start a concurrent thread for each redraw method for a smooth transition.
        Each method ends with a return statement which closes the thread as it's 
        completed (no 't.join()' required).
        """
        redraw = [redraw_window, redraw_labels, redraw_buttons, redraw_squares]
        for f in redraw:
            t = threading.Thread(target=f)
            t.start()
        return


class Frames(tk.LabelFrame):
    """Initiate and configure a LabelFrame object"""
    def __init__(self, window, bg, padx, pady, text, font, relief, border):
        super().__init__(window)
        self['bg'] = bg
        self['padx'] = padx
        self['pady'] = pady
        self['text'] = text
        self['font'] = font
        self['relief'] = relief
        self['bd'] = border


class MyLabel(tk.Label):
    """Initiate and configure a Label object"""
    def __init__(self, window, text, bg, fg, font):
        super().__init__(window)
        self['text'] = text
        self['bg'] = bg
        self['fg'] = fg
        self['font'] = font


    @staticmethod
    def place_labels(player_label, rx, ry):
        """Relative label placement (helper method)"""
        player_label.place(relx = rx, rely = ry)


class Connectivity:
    """Initiate a connection with the server"""
    def __init__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        global SOCK
        SOCK = s

        try:
            s.connect(("127.0.0.1", 9001))
        except Exception as e:
            print(e)
            return

        return


    @staticmethod
    def send_data(num):
        """Send data to the server"""

        # Keep track of the last sent value.
        # Thread terminates after each successful transmission, else
        # retry in one second.
        while True:
            try:
                data = str(num).strip()

                global last_send
                last_send = data

                data = data.encode()
                SOCK.send(data)
                return
            except Exception:
                sleep(1)


    @staticmethod
    def receive_data():
        """Receive data from the server"""
        timeout = 0

        # Keep track of the last received value.
        # Thread never terminates, unless a maximum cumulative timeout value has
        # been reached (no real fail-over option).
        while True:
            try:
                data = SOCK.recv(3).decode()

                global last_recv
                if data != last_send and data != last_recv:
                    last_recv = data
                    MyButton.main_controller(buttons_dict.get(int(data)), True)

            except Exception:
                window.title('* Cannot Establish Connection *')
                if timeout > 15:
                    break
                timeout += 1
                sleep(1)
        return


### global / constant variables ###
light_theme = {
    'BGCOLOUR': '#FEFEFE', 
    'BUTTON_COLOUR': '#B2FFD6', 
    'DISABLED_COLOUR': '#F0F0F0',
    'L_FRAME_COLOUR': '#272932'
    }

dark_mode = {
    'BGCOLOUR': '#272932',
    'BUTTON_COLOUR': '#245F6A',
    'DISABLED_COLOUR': '#4D6370',
    'L_FRAME_COLOUR': '#E7ECEF'
    }

THEME_FLIPPER = cycle([dark_mode, light_theme])
TOTAL_PLAYERS = 2
PADDING = 8
FONT = 'Gadugi 12'
BGCOLOUR = light_theme.get('BGCOLOUR')
FGCOLOUR = light_theme.get('L_FRAME_COLOUR')
RANGE = 15 # best when odd and between 11 - 15.
WINDOW_TITLE = None
SOCK = None
BUTTON_COLOUR = light_theme.get('BUTTON_COLOUR')
DISABLED_COLOUR = light_theme.get('DISABLED_COLOUR')
last_send = None
last_recv = None
buttons_dict = {}
square_dict = {}
c = 1

# Main window init call.
window = Match(BGCOLOUR, False, False, '450x500', 'A Game')

# Players configuration / initiation
try:
    for i in range(TOTAL_PLAYERS):
        if i == 0:
            Player.players.append(
                Player(f'Player {i + 1}', 0, Player.P_COLOURS[i], True)
                )
            MyLabel.place_labels(Player.players[i].name_label, 0.20, 0.86777)
            MyLabel.place_labels(Player.players[i].score_label, 0.245, 0.91777)

        else:
            Player.players.append(
                Player(f'Player {i + 1}', 0, Player.P_COLOURS[i], False)
                )
            MyLabel.place_labels(Player.players[i].name_label, 0.65, 0.86777)
            MyLabel.place_labels(Player.players[i].score_label, 0.695, 0.91777)

except IndexError:
    raise SystemExit

# Main LabelFrame init and configuration.
main_frame = Frames(
    window, BGCOLOUR, 10, 10, f"  {Player.players[0].name}'s Turn  ",
     FONT, 'sunken', 1
     )
main_frame.place(relx=0.5, rely=0.45, anchor='center')
v_sep = tk.Frame().place(relx = 0.50, rely = 0.87, relheight = 0.1)

# Theme switch button configuration.
theme_button = tk.Button(
    window, text = '■□', 
    command = lambda: Match.switch_theme(THEME_FLIPPER.__next__()), 
    font = 'Gadugi 10', bg = BGCOLOUR, relief = 'flat', cursor = 'exchange'
    )
theme_button.place(relx = 0.92, rely = 0.932)

# Generate main match board.
for i in range(RANGE):
    if i % 2 == 0:
        for j in range(RANGE):
            if j % 2 == 0:
                MyButton.make_button()
            else:
                MyButton.make_square()
            c += 1
    else:
        for j in range(RANGE):
            if j % 2 == 0:
                MyButton.make_square()
            else:
                MyButton.make_button()
            c += 1

"""
Since tkinter's mainloop can't run outside of the main Python thread,
in-order to achieve parallel socket connectivity secondary threads must
be started along side it.
I chose to use threading here because I didn't want to deal with the context-
manager's 'implicit join()', attempting to close them in event of an exception
and / or when needed in a controlled manner.
"""
act_threads = []
workers = [Connectivity, Match.window_setup, Connectivity.receive_data]

try:
    for worker in workers:
        t = threading.Thread(target=worker)
        t.start()
        act_threads.append(t)

    window.mainloop()

except Exception as e:
    raise e

finally:
    for t in act_threads:
        t.join()
    raise SystemExit
