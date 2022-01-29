import funct_local
import const_local

# initialize game rules
field_size = funct_local.get_field_size()
game_style = funct_local.get_game_style()
if game_style == 1:
    win_sequence = field_size
else:
    win_sequence = funct_local.get_win_sequence(const_local.MIN_SEQUENCE, field_size)
user_marker, pc_marker = funct_local.toss_markers()
this_turn = funct_local.toss_first()

# begin game
funct_local.clean_screen()
print(f"Начинаем игру на поле {field_size} клеток, "
      f"для победы нужно собрать линию из {win_sequence} символов. \n"
      f"Вы играете {user_marker}, компьютер играет {pc_marker}, "
      f"игру начинае{'те вы.' if this_turn == 'user' else 'т компьютер.'} "
      f"Нажмите Enter для начала игры.")
input()
funct_local.clean_screen()
field = funct_local.create_game_field(field_size)
moves_available = funct_local.create_moves_available(field)
funct_local.print_game_field(field, user_marker, pc_marker)


def execute_move(field, moves_available, logical_marker):
    field = funct_local.place_move(field, move[0], move[1], logical_marker)
    funct_local.clean_screen()
    funct_local.print_game_field(field, user_marker, pc_marker)
    moves_available.pop(move)
    moves_available = funct_local.reset_moves_rates(moves_available)
    moves_available = funct_local.count_moves_rates(field, moves_available, win_sequence)
    '''
    # explanatory part, uncomment to see logic of next pc's move
    field_explanatory = funct_local.place_rates_on_field(field, moves_available).copy()
    print()
    funct_local.print_game_field(field_explanatory, user_marker, pc_marker)
    '''


def execute_endgame():
    win = funct_local.find_win_sequence(field, win_sequence)
    if win is not None:
        if win is True:
            print("Вы победили!")
        else:
            print("Я победил!")
        victory = True
    else:
        victory = False
    if len(moves_available) == 0:
        print("Ничья!")
        victory = True
    return victory


# gameplay
victory = False
while not victory:
    if this_turn == 'user':
        move = funct_local.get_user_move(field_size)
        if move in moves_available:
            execute_move(field, moves_available, True)
            victory = execute_endgame()
            this_turn = 'pc'
        else:
            print('Выбранная клетка уже занята, нужно выбрать другую!')
            this_turn = 'user'
    else:
        move = funct_local.choose_pc_move(moves_available)
        execute_move(field, moves_available, False)
        victory = execute_endgame()
        this_turn = 'user'
print("Игра окончена...")
funct_local.sleep(3)
funct_local.abort()
