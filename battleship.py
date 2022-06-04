import os
import sys
import msvcrt as m


# max limits for board upper and lateral grid
MAX_Y = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
MAX_X = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

# lists containing the number and type (as length) of ships
SHIPS_player_1 = [4, 4, 4, 4]
SHIPS_player_2 = [4, 4, 4, 4]


def print_welcome_screen(): print("Welcome to Battleship !")


# gets the board size as width (=row) and height (=column)
def get_board_size():
    x_axis = 0
    y_axis = 0
    while True:
        pick_board_size = input('Please specifiy the board size you\'d like to play in. Minimum size is 5, maximum size is 10. Example format: 5x5 \n').casefold()
        if pick_board_size == 'quit':
            print('You have signaled the ships not to sail. See you in fairer weather !')
            sys.exit()
        pick_board_size = pick_board_size.split('x')
        if pick_board_size[0].isdigit() and pick_board_size[1].isdigit():
            x_axis, y_axis = int(pick_board_size[0]), int(pick_board_size[1])
            if ((x_axis >= 5 and x_axis <= 10) and (y_axis >= 5 and y_axis <= 10)):
                return x_axis, y_axis
            else:
                print('Please enter values between 5 and 10')
                continue
        else:
            print('Please enter the board size in the following format: [nr]x[nr]  ex 5x5')
            continue


# generates the initial blank board that is filled with 0's
def generate_board(x_axis, y_axis):
    blank_board = []
    for board_y_axis in range(y_axis):
        blank_board.append([])
        for board_x_axis in range(x_axis):
            blank_board[board_y_axis].append('0')
    return blank_board


def print_game_board(board, x_axis, y_axis):
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    for x in range(1, x_axis + 1):
        print('  ', x, end=" ")
    print('\t')
    print(' ' + '  ---' * x_axis)
    for slot in range(len(board)):
        print(alphabet[slot] + ' | ' + '    '.join(board[slot]) + ' | ')
    print(' ' + '  ---' * x_axis)


def deliver_ship_placement_instructions(): print('You can now start placing your ships.')


# function to validate if the input constitutes a position on the board; ONLY validates format, doesn't check contents
def validate_input_position(board, x_axis, y_axis):
    x_axis_range = MAX_X[0:(x_axis)]
    y_axis_range = MAX_Y[0:(y_axis)]
    chosen_position = input('Please choose a valid position on the board in the format [number]-[letter] ex A-1 \n')
    while True:
        if chosen_position.casefold() == 'quit':
            print('You have decided to quit the game. I\'ll await with calmer weather')
            sys.exit()
        chosen_position = chosen_position.split('-')
        if chosen_position[0].upper() in y_axis_range and chosen_position[1] in x_axis_range:
            x_axis, y_axis = y_axis_range.index(chosen_position[0].upper()), x_axis_range.index(chosen_position[1])
            return x_axis, y_axis
        else:
            chosen_position = input('Position not found, try again \n')


def offer_turn_limit():
    print('You have the option to set a number of turns for the game')
    while True:
        user_choice = input('Do you wish to set a number of turns? (Yes / No)\n').lower()
        if user_choice == 'yes':
            turn_limit = input('Please select between 5 and 50 turns\n')
            if turn_limit.isnumeric():
                if 5 <= int(turn_limit) <= 50:
                    return int(turn_limit)
                else:
                    print('Sorry, I didn\'t get that, please type a number from 5 to 50\n')
                    continue
        elif user_choice == 'no':
            print('Alright, you will play without a fixed number of turns')
            return False
        elif user_choice.lower() == 'quit':
            print('You have decided not to go to war afterall, regards !')
            sys.exit()
        else:
            print('Sorry, I didn\'t get that, please state Yes or No\n')
            continue


def present_ship_direction_instructions():
    print('Please select the direction you\'d like the ship to be placed towards\n')
    print('N for North (ship will head towards the bottom of the board)')
    print('S for South (ship will head towards the top of the board)')
    print('E for East (ship will head towards the left side of the board)')
    print('W for West (ship will head towards the right side of the board)')


# function to draw the rest of the ship in the specified direction
def draw_ship_in_direction(direction, ship_length, board, ship_head_x_axis, ship_head_y_axis, x_axis_max, y_axis_max):
    ship_mark = 'X'
    aura_mark = 'C'
    fringe_limit_x = x_axis_max - 1
    fringe_limit_y = y_axis_max - 1
    try:
        if direction == 'N':
            if ship_head_x_axis - ship_length < 0:
                return 0
            if ship_head_x_axis - ship_length - 1 >= 0:
                if board[ship_head_x_axis + 1 - ship_length][ship_head_y_axis] == 'C':
                    return False
            if ship_head_x_axis - 1 >= 0:
                board[ship_head_x_axis - 1][ship_head_y_axis] = 'T'  # places the first connecting ship segment (removes from enveloping aura)
            if ship_head_x_axis - ship_length >= 0:
                if board[ship_head_x_axis + 1 - ship_length][ship_head_y_axis] == 'X':  # check if end segment collides with another ship [ship_head_x_axis - ship_length]
                    return False
                place_mark_on_board(board, (ship_head_x_axis - ship_length), ship_head_y_axis, aura_mark)  # places the endpoint aura mark
            for segment in range(1, ship_length):
                if ship_head_x_axis - segment >= 0:
                    place_mark_on_board(board, (ship_head_x_axis - segment), ship_head_y_axis, ship_mark) # places ship segments
                    if ((ship_head_y_axis + 1) <= fringe_limit_x and board[ship_head_x_axis - segment][ship_head_y_axis + 1] == 'X'):  # check if right-side ship tangent
                        return False
                    else:
                        if ((ship_head_x_axis - segment >= 0) and ((ship_head_y_axis + 1) <= fringe_limit_x)):
                            place_mark_on_board(board, (ship_head_x_axis - segment), (ship_head_y_axis + 1), aura_mark)  # right-side aura placement  (ship_head_y_axis + 1)
                    if board[ship_head_x_axis - segment][ship_head_y_axis - 1] == 'X':  # check if left-side ship tangent
                        return False
                    else:
                        if (ship_head_x_axis - segment) >= 0 and (ship_head_y_axis - 1) >= 0:
                            place_mark_on_board(board, (ship_head_x_axis - segment), (ship_head_y_axis - 1), aura_mark)  # left-side aura placement
                else: return False
            return board
        elif direction == 'S':
            if ship_head_x_axis + ship_length > fringe_limit_x:
                return 0
            if ship_head_x_axis + ship_length + 1 <= fringe_limit_x:
                if board[ship_head_x_axis + 1 + ship_length][ship_head_y_axis] == 'C':
                    return False
            if ship_head_x_axis + 1  <= fringe_limit_y:                 
                board[ship_head_x_axis + 1][ship_head_y_axis] = 'T'
            if (ship_head_x_axis + ship_length) <= fringe_limit_y:
                if board[ship_head_x_axis + ship_length - 1][ship_head_y_axis] == 'X':
                    return False
                place_mark_on_board(board, (ship_head_x_axis + ship_length), ship_head_y_axis, aura_mark)
            for segment in range(1, ship_length):
                if (ship_head_x_axis + ship_length - 1) <= fringe_limit_y:
                    place_mark_on_board(board, (ship_head_x_axis + segment), ship_head_y_axis, ship_mark)
                    if ((ship_head_y_axis + 1) <= fringe_limit_x and board[ship_head_x_axis + segment][ship_head_y_axis + 1]) == 'X':
                        return False
                    else:
                        if (ship_head_x_axis + segment) and ((ship_head_y_axis + 1) <= fringe_limit_x):
                            place_mark_on_board(board, (ship_head_x_axis + segment), (ship_head_y_axis + 1), aura_mark)
                    if board[ship_head_x_axis + segment][ship_head_y_axis - 1] == 'X':
                        return 0
                    else:
                        if (ship_head_x_axis + segment) and (ship_head_y_axis - 1) >= 0:
                            place_mark_on_board(board, (ship_head_x_axis + segment), (ship_head_y_axis - 1), aura_mark)
                else: return False
            return board
        elif direction == 'E':
            if ship_head_y_axis + ship_length > fringe_limit_y:
                return False
            if ship_head_y_axis + ship_length + 1 <= fringe_limit_y:
                if board[ship_head_x_axis][ship_head_y_axis + ship_length - 1] == 'C':
                    return False
            if ship_head_y_axis + 1 <= fringe_limit_x:
                board[ship_head_x_axis][ship_head_y_axis + 1] = 'T'
            if (ship_head_y_axis + ship_length) <= fringe_limit_x:
                if board[ship_head_x_axis][ship_head_y_axis + ship_length - 1] == 'X':
                    return False
                place_mark_on_board(board, ship_head_x_axis, (ship_head_y_axis + ship_length), aura_mark)
            for segment in range(1, ship_length):
                if (ship_head_y_axis + ship_length - 1) <= fringe_limit_x:
                    place_mark_on_board(board, ship_head_x_axis, (ship_head_y_axis + segment), ship_mark)
                    if ((ship_head_x_axis + 1) <= fringe_limit_y and board[ship_head_x_axis + 1][ship_head_y_axis + segment] == 'X'):
                        return False
                    else:
                        if (ship_head_y_axis + segment) and ((ship_head_x_axis + 1) <= fringe_limit_x):
                            place_mark_on_board(board, (ship_head_x_axis + 1), (ship_head_y_axis + segment), aura_mark)
                    if board[ship_head_x_axis - 1][ship_head_y_axis + segment] == 'X':
                        return False
                    else:
                        if (ship_head_y_axis + segment) and (ship_head_x_axis - 1) > 0:
                            place_mark_on_board(board, (ship_head_x_axis - 1), (ship_head_y_axis + segment), aura_mark)
                else: return False
            return board
        elif direction == 'W':
            if ship_head_y_axis - ship_length < 0:
                return False
            if ship_head_y_axis - ship_length - 1 >= 0:
                if board[ship_head_x_axis][ship_head_y_axis - ship_length + 1] == 'C':
                    return False
            if ship_head_y_axis - 1 >= 0:
                board[ship_head_x_axis][ship_head_y_axis - 1] = 'T'
            if (ship_head_y_axis - ship_length) >= 0:
                if board[ship_head_x_axis][ship_head_y_axis + 1 - ship_length] == 'X':
                    return False
                place_mark_on_board(board, ship_head_x_axis, (ship_head_y_axis - ship_length), aura_mark)
            for segment in range(1, ship_length):
                if (ship_head_y_axis - segment) >= 0:
                    place_mark_on_board(board, ship_head_x_axis, (ship_head_y_axis - segment), ship_mark)
                    if ((ship_head_x_axis + 1) <= fringe_limit_y and board[ship_head_x_axis + 1][ship_head_y_axis - segment] == 'X'):
                        return False
                    else:
                        if (ship_head_y_axis - segment) and ((ship_head_x_axis + 1) <= fringe_limit_x):
                            place_mark_on_board(board, (ship_head_x_axis + 1), (ship_head_y_axis - segment), aura_mark)
                    if board[ship_head_x_axis - 1][ship_head_y_axis - segment] == 'X':
                        return False
                    else:
                        if (ship_head_y_axis - segment) and ((ship_head_x_axis - 1) > 0):
                            place_mark_on_board(board, (ship_head_x_axis - 1), (ship_head_y_axis - segment), aura_mark)
                else: return False
            return board
    except IndexError():
        return False


# gets the direction from the user
def validate_ship_direction():
    ship_direction = input('Type N, S, E or W \n').upper()
    while True:
        if ship_direction == 'N' or ship_direction == 'S' or ship_direction == 'E' or ship_direction == 'W':
            return ship_direction
        else:
            ship_direction = input('Please type N, S, E or W \n').upper()


# function to place any kind of mark on the board, as long as the place is available for specified purposes
def place_mark_on_board(board, x_axis, y_axis, mark):
    if board[x_axis][y_axis] == '0':
        board[x_axis][y_axis] = mark
        return board
    elif board[x_axis][y_axis] == 'C' and mark == 'C':  # ships can share auras
        board[x_axis][y_axis] = mark
        return board
    elif board[x_axis][y_axis] == 'X' and mark == '0':
        board[x_axis][y_axis] = mark
        return board
    elif board[x_axis][y_axis] == 'T' and mark == 'X':
        board[x_axis][y_axis] = mark
        return board
    elif board[x_axis][y_axis] == 'X' and mark == 'X':
        return False
    elif board[x_axis][y_axis] == 'C' and mark == 'X':
        return False
    else:
        return False


def ship_head_aura(board, x_axis, y_axis, mark, x_axis_max, y_axis_max):
    fringe_limit_x = x_axis_max - 1
    fringe_limit_y = y_axis_max - 1
    if x_axis == 0 and y_axis == 0:
        if board[x_axis + 1][y_axis] == 'X' or board[x_axis][y_axis + 1] == 'X':
            return False
        else:
            board[x_axis + 1][y_axis] = mark
            board[x_axis][y_axis + 1] = mark
        return board
    elif x_axis == 0 and y_axis == fringe_limit_x:
        if board[x_axis][y_axis - 1] == 'X' or board[x_axis + 1][y_axis] == 'X':
            return False
        else:
            board[x_axis][y_axis - 1] = mark
            board[x_axis + 1][y_axis] = mark
        return board
    elif x_axis == fringe_limit_y and y_axis == 0:
        if board[x_axis - 1][y_axis] == 'X' or board[x_axis][y_axis + 1] == 'X':
            return False
        else:
            board[x_axis - 1][y_axis] = mark
            board[x_axis][y_axis + 1] = mark
        return board
    elif x_axis == fringe_limit_y and y_axis == fringe_limit_x:
        if board[x_axis][y_axis - 1] == 'X' or board[x_axis - 1][y_axis] == 'X':
            return False
        else:
            board[x_axis][y_axis - 1] = mark
            board[x_axis - 1][y_axis] = mark
        return board
    elif x_axis == 0:
        if board[x_axis][y_axis - 1] == 'X' or board[x_axis][y_axis + 1] == 'X' or board[x_axis + 1][y_axis] == 'X':
            return False
        else:
            board[x_axis][y_axis - 1] = mark
            board[x_axis][y_axis + 1] = mark
            board[x_axis + 1][y_axis] = mark
        return board
    elif y_axis == 0:
        if board[x_axis + 1][y_axis] == 'X' or board[x_axis - 1][y_axis] == 'X' or board[x_axis][y_axis + 1] == 'X':
            return False
        else:
            board[x_axis + 1][y_axis] = mark
            board[x_axis - 1][y_axis] = mark
            board[x_axis][y_axis + 1] = mark
        return board
    elif y_axis == fringe_limit_x:
        if board[x_axis + 1][y_axis] == 'X' or board[x_axis - 1][y_axis] == 'X' or board[x_axis][y_axis - 1] == 'X':
            return False
        else:
            board[x_axis + 1][y_axis] = mark
            board[x_axis - 1][y_axis] = mark
            board[x_axis][y_axis - 1] = mark
        return board
    elif x_axis == fringe_limit_y:
        if board[x_axis][y_axis + 1] == 'X' or board[x_axis][y_axis - 1] == 'X' or board[x_axis - 1][y_axis] == 'X':
            return False
        else:
            board[x_axis][y_axis + 1] = mark
            board[x_axis][y_axis - 1] = mark
            board[x_axis - 1][y_axis] = mark
        return board
    else:
        if board[x_axis + 1][y_axis] == 'X' or board[x_axis - 1][y_axis] == 'X' or board[x_axis][y_axis + 1] == 'X' or board[x_axis][y_axis - 1] == 'X':
            return False
        else:
            board[x_axis + 1][y_axis] = mark
            board[x_axis - 1][y_axis] = mark
            board[x_axis][y_axis + 1] = mark
            board[x_axis][y_axis - 1] = mark
        return board


def get_ship_placement(board, ship_list, x_axis, y_axis, x_axis_max, y_axis_max):
    marked_board = generate_board(x_axis, y_axis)
    x_axis_max = x_axis
    y_axis_max = y_axis
    ship_mark = 'X'
    empty_spot = '0'
    keep_ship_coordinates = dict()
    count_ships = 0
    for ship in ship_list:
        keep_ship_coordinates[ship] = None
    while ship_list:
        current_ship_length = ship_list[0]
        print(f'The current ship you have to place is {ship_list[0]} squares long')
        print('Please select the area for the \'head\' of the ship (starting position)\n')
        ship_head_x_axis, ship_head_y_axis = validate_input_position(marked_board, x_axis, y_axis)
        print(ship_head_x_axis, ship_head_y_axis)
        if marked_board[ship_head_x_axis][ship_head_y_axis] != '0':
            print('Please select a valid position. The position you selected seems to be occupied')
            ship_head_x_axis, ship_head_y_axis = validate_input_position(marked_board, x_axis, y_axis)
        place_mark_on_board(marked_board, ship_head_x_axis, ship_head_y_axis, ship_mark)
        if ship_head_aura(marked_board, ship_head_x_axis, ship_head_y_axis, 'C', x_axis_max, y_axis_max):
            marked_board = ship_head_aura(marked_board, ship_head_x_axis, ship_head_y_axis, 'C', x_axis_max, y_axis_max)
            print_game_board(marked_board, x_axis, y_axis)
            present_ship_direction_instructions()
            ship_generation_direction = validate_ship_direction()
            if draw_ship_in_direction(ship_generation_direction, current_ship_length, marked_board, ship_head_x_axis, ship_head_y_axis, x_axis_max, y_axis_max):
                keep_ship_coordinates[count_ships] = [ship_head_x_axis, ship_head_y_axis, ship_generation_direction]
                ship_list.pop(0)
                count_ships += 1
                print_game_board(marked_board, x_axis, y_axis)
            else:
                print('\nShip positioning failed: out of bounds or ship is tangent to another ship. Restarting placement of ship \n')
                marked_board = place_mark_on_board(marked_board, ship_head_x_axis, ship_head_y_axis, empty_spot)
                marked_board = ship_head_aura(marked_board, ship_head_x_axis, ship_head_y_axis, empty_spot, x_axis_max, y_axis_max)
                print('\nBoard currently contains : \n')
                print_game_board(marked_board, x_axis, y_axis)
                continue
        else:
            print('\nShip head positioning failed: too close to another ship. Restarting ship head placement\n')
            place_mark_on_board(marked_board, ship_head_x_axis, ship_head_y_axis, empty_spot)
            continue

    return marked_board, keep_ship_coordinates


# clears screen
def console_clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# waits for any key press to continue
def wait_for_any_input():
    print('\n Press any key to continue\n')
    m.getch()


def announce_next_player():
    print('\nPlayer 2, prepare your battleships !\n')
    wait_for_any_input()


def announce_shooting_phase():
    print('Let the battle commence ! Player 1, aim your cannons !')


def shooting_board_marking(enemy_board, play_board, x_axis, y_axis):
    if play_board[x_axis][y_axis] == '0' and enemy_board[x_axis][y_axis] == 'X':
        play_board[x_axis][y_axis] = 'H'
        print('\n Ship has been Hit ! \n')
        return play_board
    elif play_board[x_axis][y_axis] == '0' and enemy_board[x_axis][y_axis] == '0':
        play_board[x_axis][y_axis] = 'W'
        print('It appears you have hit a patch of water...')
        return play_board
    elif play_board[x_axis][y_axis] != '0':
        return False


def win_condition(board, ship_list, x_axis, y_axis):
    sum_of_segments = 0
    sum_of_H = 0
    SHIPS_player_1 = [4, 4, 4, 4]
    ship_list = SHIPS_player_1
    for ship in ship_list:
        sum_of_segments += ship
    for nest in range(y_axis):
        for egg in range(x_axis):
            if board[nest][egg] == 'H':
                sum_of_H += 1
    if (sum_of_H == sum_of_segments):
        return 'True'
    else:
        return 'False'


def play_shoot_ship(player, play_board, enemy_board, x_axis, y_axis, ship_list):
    print(f'It\'s {player}\'s turn to attack !\n')
    print_game_board(play_board, x_axis, y_axis)
    player_move_x, player_move_y = validate_input_position(play_board, x_axis, y_axis)
    if not shooting_board_marking(enemy_board, play_board, player_move_x, player_move_y):
        print('You have already tried that position, please pick another')
        print_game_board(play_board, x_axis, y_axis)
        player_move_x, player_move_y = validate_input_position(play_board, x_axis, y_axis)
    else:
        print_game_board(play_board, x_axis, y_axis)
        return play_board


def announce_winner(player):
    print('{} has won!!!'.format(player))
    sys.exit()


def test_main_game_flow():
    player1 = 'Player 1'
    player2 = 'Player 2'
    print_welcome_screen()
    current_x_axis, current_y_axis = get_board_size()
    current_x_fringe_limit = current_x_axis
    current_y_fringe_limit = current_y_axis
    blank_board = generate_board(current_x_axis, current_y_axis)
    print_game_board(blank_board, current_x_axis, current_y_axis)
    player1_play_board = generate_board(current_x_axis, current_y_axis)
    player2_play_board = generate_board(current_x_axis, current_y_axis)
    play_with_turns = offer_turn_limit()
    deliver_ship_placement_instructions()
    ships_player_1_board, ships_player_1_locations = get_ship_placement(blank_board, SHIPS_player_1, current_x_axis, current_y_axis, current_x_fringe_limit, current_x_fringe_limit)
    # console_clear()     # to be uncommented when actual gameplay happens
    announce_next_player()
    wait_for_any_input()
    deliver_ship_placement_instructions()
    print_game_board(blank_board, current_x_axis, current_y_axis)
    ships_player_2_board, ships_player_2_locations = get_ship_placement(blank_board, SHIPS_player_2, current_x_axis, current_y_axis, current_x_fringe_limit, current_y_fringe_limit)
    console_clear()
    announce_shooting_phase()
    if play_with_turns:
        counter = play_with_turns
        while counter:
            player1_play_board = play_shoot_ship(player1, player1_play_board, ships_player_2_board, current_x_axis, current_y_axis, SHIPS_player_1)
            if win_condition(player1_play_board, SHIPS_player_1, current_x_axis, current_y_axis) == 'True':
                announce_winner(player1)
            else:
                player2_play_board = play_shoot_ship(player2, player2_play_board, ships_player_1_board, current_x_axis, current_y_axis, SHIPS_player_2)
                if win_condition(player2_play_board, SHIPS_player_1, current_x_axis, current_y_axis) == 'True':
                    announce_winner(player2)
                counter = counter-1
            if counter == 0:
                print('You have expended the number of moves, it\'s a tie')
                break
    else:
        while True:
            player1_play_board = play_shoot_ship(player1, player1_play_board, ships_player_2_board, current_x_axis, current_y_axis, SHIPS_player_1)
            if win_condition(player1_play_board, SHIPS_player_1, current_x_axis, current_y_axis) == 'True':
                announce_winner(player1)
            else:
                player2_play_board = play_shoot_ship(player2, player2_play_board, ships_player_1_board, current_x_axis, current_y_axis, SHIPS_player_2)
                if win_condition(player2_play_board, SHIPS_player_1, current_x_axis, current_y_axis) == 'True':
                    announce_winner(player2)



if __name__ == '__main__':
    SHIPS_player_1 = [4, 4, 4, 4]
    SHIPS_player_2 = [4, 4, 4, 4]
    test_main_game_flow()
