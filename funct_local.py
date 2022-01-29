import const_local
from platform import system as os
from os import system
from sys import exit as abort
from time import sleep
from random import choice


# decorate input functions to limit acceptable number of incorrect user inputs
def limit_attempts(func):
    attempt = 0

    def wrapper(*args):
        nonlocal attempt
        if attempt < const_local.INPUT_ATTEMPTS:
            attempt += 1
            return func(*args)
        else:
            print(f'Превышено количество попыток ввода, игра завершается...')
            sleep(3)
            abort()

    return wrapper


# recursively request from user the game field size until correct input or limit is reached
@limit_attempts
def get_field_size():
    field_side = int(input(f"Выберите размер игрового поля от "
                           f"{const_local.MIN_FIELD} до {const_local.MAX_FIELD}:\n"))
    if const_local.MAX_FIELD >= field_side >= const_local.MIN_FIELD:
        return field_side
    else:
        print('Введено неверное значение!')
        return get_field_size()


# recursively request from user the game style (or type) until correct input or limit is reached
@limit_attempts
def get_game_style():
    game_style = int(input("Выберите игровой режим:\n"
                           "[1] обычный\n"
                           "[2] N в ряд (Gomoku)\n"))
    if game_style in const_local.GAME_STYLES:
        return game_style
    else:
        print('Введено неверное значение!')
        return get_game_style()


# recursively request from user the length of symbols in one line which means victory
@limit_attempts
def get_win_sequence(min, max):
    win_sequence = int(input(f"Введите длину победной комбинации от {min} до {max}:\n"))
    if min <= win_sequence <= max:
        return win_sequence
    else:
        print('Введено неверное значение!')
        return get_win_sequence(min, max)


# recursively request from user his move and return parsed tuple (row: int, col: str)
def get_user_move(limit):
    move = input(f"\nВаш ход!\n").upper().replace(" ", "")
    if move[0].isalpha():
        col = move[0]
        if move[1:].isdigit():
            row = int(move[1:])
        else:
            print('Введено неверное значение!')
            return get_user_move(limit)
    elif move[-1].isalpha():
        col = move[-1]
        if move[0:-1].isdigit():
            row = int(move[0:-1])
        else:
            print('Введено неверное значение!')
            return get_user_move(limit)
    else:
        print('Введено неверное значение!')
        return get_user_move(limit)
    if row in range(1, limit + 1) and col in const_local.COLUMN_NAMES[1:limit + 1]:
        return row, col
    else:
        print('Значение за пределами игрового поля!')
        return get_user_move(limit)


# randomly return markers for player and pc
def toss_markers():
    user_marker = choice(const_local.MARKERS)
    pc_marker = list(set(const_local.MARKERS).difference({user_marker}))[0]
    return user_marker, pc_marker


# randomly selects who starts with first move
def toss_first():
    return choice(const_local.PLAYERS)


# create empty game field
# game field itself will be the list of dicts:
# each list item is a single horizontal row => rows are numbered,
# in each dict keys are same letters from A => columns are lettered
def create_game_field(size):
    row = {}
    for i in range(size + 1):
        row[const_local.COLUMN_NAMES[i]] = None
    field = []
    for i in range(size + 1):
        field.append(row.copy())  # perfect place to get stuck - simple .append() fills list with dicts with same id
    for i in range(size + 1):
        if i == 0:
            for j in const_local.COLUMN_NAMES[:size + 1]:
                field[i][j] = j
        field[i][const_local.COLUMN_NAMES[0]] = i
    return field


# convert a dictionary into string with formatted spaces
def glue_dict(dic, user_marker, pc_marker):
    result = ""
    for i in dic.keys():
        if result != "":
            if dic[i] is None:
                result += f"{const_local.EMPTY_CELL:^3}"
            elif dic[i] is True:
                result += f"{user_marker:^3}"
            elif dic[i] is False:
                result += f"{pc_marker:^3}"
            else:
                result += f"{str(dic[i]):^3}"
        else:
            result += f"{str(dic[i]):>3} "
    return result


# get list of keys of dict where values are equal to defined
def keys_dict(dic, value):
    result = []
    for i in dic.items():
        if i[1] == value:
            result.append(i[0])
    return result


# print current game field state
def print_game_field(field, user_marker, pc_marker):
    for i in field:
        print(glue_dict(i, user_marker, pc_marker))


# place move on field, return modified game field
def place_move(field, row, col, value):
    field[row][col] = value
    return field


# create dict of available moves
# keys are tuples (row: int, col: str)
# values will be counted separately on each pc move and will reflect the rating of occupation of related cell
def create_moves_available(field):
    moves_available = {}
    for i in field:
        for j in i:
            if i[j] is None:
                moves_available[(field.index(i), j)] = 0
    return moves_available


# before counting moves rates on current stage of the game, reset previously counted
def reset_moves_rates(moves_available):
    for i in moves_available:
        moves_available[i] = 0
    return moves_available


# count moves rates, return modified moves_available
def count_moves_rates(field, moves_available, win_sequence):
    for start in moves_available:
        for direction in range(1, 9):
            for length in range(1, win_sequence):
                exists = find_sequence(field, start, length, direction)
                if exists is not None:
                    moves_available[start] += length ** (4 if exists is True else 3)
                else:
                    break
    return moves_available


# choose best available move or random move from one of the best
def choose_pc_move(moves_available):
    variants = moves_available.values()
    top_variant = max(variants)
    return choice(keys_dict(moves_available, top_variant))


# demonstrational - show moves rates on game field, should be applied to copy of field
# return modified field describing the values of moves
def place_rates_on_field(field, moves_available):
    mfield = create_game_field(len(field) - 1)
    for place in moves_available:
        mfield[place[0]][place[1]] = moves_available[place]
    return mfield


# sequence directions are numbers presumed as following:
# ======================================================
#                     8    1      2
#                      \   |     /
#                       \  |   /
#                        \ | /
#                7 --------*-------- 3
#                        / | \
#                      /   |  \
#                    /     |   \
#                   6      5    4
# ======================================================

# check if sequence of (length: int) is possible from start (row: int, col: str) position
# (start position itself is not included) on (field) in (direction: int) (see directions' description above)
# return True if sequence is possible and False if end of sequence is out of game field
def sequence_is_possible(field, start, length, direction):
    field_size = len(field) - 1
    if direction == 1:
        return True if (start[0] - length > 0) else False
    elif direction == 2:  # is combination of 1 and 3 cases, both should return True
        return True if ((start[0] - length > 0) and
                        (const_local.COLUMN_NAMES.index(start[1]) + length <= field_size)) else False
    elif direction == 3:
        return True if (const_local.COLUMN_NAMES.index(start[1]) + length <= field_size) else False
    elif direction == 4:  # is combination of 3 and 5 cases, both should return True
        return True if ((start[0] + length <= field_size) and
                        (const_local.COLUMN_NAMES.index(start[1]) + length <= field_size)) else False
    elif direction == 5:
        return True if (start[0] + length <= field_size) else False
    elif direction == 6:  # is combination on 5 and 7 cases, both should return True
        return True if ((start[0] + length <= field_size) and
                        (const_local.COLUMN_NAMES.index(start[1]) - length > 0)) else False
    elif direction == 7:
        return True if (const_local.COLUMN_NAMES.index(start[1]) - length > 0) else False
    elif direction == 8:  # is combination of 7 and 1 cases, both should return True
        return True if ((start[0] - length > 0) and
                        (const_local.COLUMN_NAMES.index(start[1]) - length > 0)) else False


# check if sequence of (length: int) exists from start (row: int, col: str) position
# (start position itself is not included) on (field) in (direction: int) (see directions' description above)
# return True if sequence of values 'True' exists
# return False if sequence of values 'False' exists
# return None if no uninterrupted sequence exists (including case when such sequence is not possible)
def find_sequence(field, start, length, direction):
    if sequence_is_possible(field, start, length, direction):
        cells_values = []  # collect all cells' values from field from start not including start itself
        for i in range(1, length + 1):
            if direction == 1:
                cells_values.append(field[start[0] - i][start[1]])
            elif direction == 2:  # is combination of 1 and 3 cases
                cells_values.append(field[start[0] - i]
                                    [const_local.COLUMN_NAMES[const_local.COLUMN_NAMES.index(start[1]) + i]])
            elif direction == 3:
                cells_values.append(field[start[0]]
                                    [const_local.COLUMN_NAMES[const_local.COLUMN_NAMES.index(start[1]) + i]])
            elif direction == 4:  # is combination of 3 and 5 cases
                cells_values.append(field[start[0] + i]
                                    [const_local.COLUMN_NAMES[const_local.COLUMN_NAMES.index(start[1]) + i]])
            elif direction == 5:
                cells_values.append(field[start[0] + i][start[1]])
            elif direction == 6:  # is combination on 5 and 7 cases
                cells_values.append(field[start[0] + i]
                                    [const_local.COLUMN_NAMES[const_local.COLUMN_NAMES.index(start[1]) - i]])
            elif direction == 7:
                cells_values.append(field[start[0]]
                                    [const_local.COLUMN_NAMES[const_local.COLUMN_NAMES.index(start[1]) - i]])
            elif direction == 8:  # is combination of 7 and 1 cases
                cells_values.append(field[start[0] - i]
                                    [const_local.COLUMN_NAMES[const_local.COLUMN_NAMES.index(start[1]) - i]])
        cells_values = set(cells_values)  # leave only unique values from initially collected list
        if (len(cells_values) == 1) and (None not in cells_values):
            return list(cells_values)[0]
        else:
            return None
    else:
        return None


def find_win_sequence(field, win_sequence):
    for i in field:
        for j in i:
            if i[j] is None:
                continue
            else:
                for direction in range (2, 6):
                    attempt = find_sequence(field, (field.index(i), j), win_sequence - 1, direction)
                    if i[j] is attempt:
                        return attempt
    return None


# clean the console depending on operation system type
def clean_screen():
    sys = os()
    if sys == 'Linux':
        system('clear')
    elif sys == 'Windows':
        system('cls')
    else:
        for i in range(100):
            print('\n')
