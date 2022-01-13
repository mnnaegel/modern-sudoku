import arcade
import settings
import math
import random
import pickle
from time import strftime, gmtime
import copy
from typing import List, Dict, Tuple, Union, Set


WIDTH = settings.WIDTH
HEIGHT = settings.HEIGHT

data: List["Winner"] = []
user = None
winner = None
game = None
game_view = None


def translate_symbol(symbol: int) -> Union[str, None]:
    """ translates symbols of keyboard inputs to corresponding values
    Args:
        symbol: numerical symbol represnting a keyboard input
    Returns:
        The corresponding value of the symbol or None if not in translator
    """
    symbol_translator = {
        48: '0',
        49: '1',
        50: '2',
        51: '3',
        52: '4',
        53: '5',
        54: '6',
        55: '7',
        56: '8',
        57: '9',
        95: '_',
        97: 'A',
        98: 'B',
        99: 'C',
        100: 'D',
        101: 'E',
        102: 'F',
        103: 'G',
        104: 'H',
        105: 'I',
        106: 'J',
        107: 'K',
        108: 'L',
        109: 'M',
        110: 'N',
        111: 'O',
        112: 'P',
        113: 'Q',
        114: 'R',
        115: 'S',
        116: 'T',
        117: 'U',
        118: 'V',
        119: 'W',
        120: 'X',
        121: 'Y',
        122: 'Z'
    }

    try:
        return symbol_translator[symbol]
    except KeyError:
        return None


def save_data() -> None:
    global data
    """ Saves data of all winners into sudoku_data.p
    Args:
        None
    Returns:
        None
    """
    with open("sudoku_data.p", "wb") as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


def load_data() -> None:
    global data
    """ Loads data of all winners into sudoku_data.p
    Args:
        None
    Returns:
        None
    """

    with open("sudoku_data.p", "rb") as f:
        data = pickle.load(f)


class Sudoku:
    """ Sudoku game class

    Attrs:
        _ALL_START_BOARDS(List[List[List[int]]]): all sudoku game boards
        _start_board(List[List[int]]): a randomized sudoku gameboard
        _board(List[List[int]]): game board where the user can input numbers
        _columns(int): the amount of columns in the board
        _rows(int): the amount of rows in the board
        _selected(Tuple[int, int]): most recently clicked board coordinate
        _temp_board(Dict[Tuple, List]): game board with temporary values
        _x_gap(int): the gap between vertical grid lines
        _y_gap(int): the gap between horizontal grid lines
        _pencil_mode(bool): the status of pencil tool's activation
        _incorrect_coordinates(List[Tuple[int, int]]): list of coordinates
                                                       with invalid numbers
        _validate_button("Sprite"): calls the validate function when pressed
        _validate_button.texture("texture"): the validate button's texture
        _solve_button("Sprite"): calls the solve function when pressed
        _solve_button.texture("texture"): the solve button's texture
        _reset_button("Sprite"): calls the reset function when pressed
        _reset_button.texture("texture"): the reset button's texture
        _pencil_button("Sprite"): toggles pencil mode on/off when pressed
        _pencil_button.texture("texture"): the pencil button's texture

    """

    _ALL_START_BOARDS: List[List[List[int]]] = [
        [
            [7, 8, 0, 4, 0, 0, 1, 2, 0],
            [6, 0, 0, 0, 7, 5, 0, 0, 9],
            [0, 0, 0, 6, 0, 1, 0, 7, 8],
            [0, 0, 7, 0, 4, 0, 2, 6, 0],
            [0, 0, 1, 0, 5, 0, 9, 3, 0],
            [9, 0, 4, 0, 6, 0, 0, 0, 5],
            [0, 7, 0, 3, 0, 0, 0, 1, 2],
            [1, 2, 0, 0, 0, 7, 4, 0, 0],
            [0, 4, 9, 2, 0, 6, 0, 0, 7]
        ],
        [
            [0, 4, 0, 8, 0, 5, 2, 0, 0],
            [0, 2, 0, 0, 4, 0, 0, 5, 0],
            [5, 0, 0, 0, 0, 0, 0, 0, 4],
            [0, 9, 0, 0, 0, 3, 1, 2, 0],
            [1, 0, 6, 0, 7, 8, 0, 0, 3],
            [3, 7, 0, 9, 0, 4, 0, 8, 0],
            [0, 0, 0, 0, 0, 6, 7, 0, 0],
            [0, 0, 8, 3, 5, 9, 0, 1, 0],
            [0, 1, 9, 0, 0, 7, 6, 0, 0]
        ],

        [
            [0, 6, 0, 3, 0, 0, 8, 0, 4],
            [5, 3, 7, 0, 9, 0, 0, 0, 0],
            [0, 4, 0, 0, 0, 6, 3, 0, 7],
            [0, 9, 0, 0, 5, 1, 2, 3, 8],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [7, 1, 3, 6, 2, 0, 0, 4, 0],
            [3, 0, 6, 4, 0, 6, 0, 1, 0],
            [0, 0, 0, 0, 6, 0, 5, 2, 3],
            [1, 0, 2, 0, 0, 9, 0, 8, 0]
        ]
    ]

    def __init__(self, start_board: List[List[int]]) -> None:
        """ Creates a sudoku game

        Args:
            start_board: a randomized sudoku game board

        """
        self._start_board = start_board
        self._columns: int = 9
        self._rows: int = 9
        self._board: List[List[int]] = copy.deepcopy(start_board)
        self._selected: Tuple[int, int] = (math.ceil(self._columns / 2),
                                           math.ceil(self._rows / 2))
        self._temp_board: Dict[Tuple, List] = {(i, j): []
                                               for i in range(self._columns)
                                               for j in range(self._rows)}
        self._x_gap: float = WIDTH / self._columns
        self._y_gap: float = HEIGHT / self._rows
        self._pencil_mode: bool = False
        self._incorrect_coordinates: List[Tuple[int, int]] = []
        self._validate_button: "Sprite" = arcade.Sprite(center_x=133.33,
                                                        center_y=50)
        self._validate_button.texture: "texture" = arcade.make_soft_circle_texture(65,
                                                                                   arcade.color.LIGHT_SLATE_GRAY,
                                                                                   outer_alpha=255)
        self._solve_button: "Sprite" = arcade.Sprite(center_x=666.66,
                                                     center_y=50)
        self._solve_button.texture: "texture" = arcade.make_soft_circle_texture(65,
                                                                                arcade.color.LIGHT_SLATE_GRAY,
                                                                                outer_alpha=255)
        self._reset_button: "Sprite" = arcade.Sprite(center_x=751.5,
                                                     center_y=575)
        self._reset_button.texture: "texture" = arcade.make_soft_circle_texture(37,
                                                                                arcade.color.LIGHT_SLATE_GRAY,
                                                                                outer_alpha=255)
        self._pencil_button: "Sprite" = arcade.Sprite(center_x=400,
                                                      center_y=50)
        self._pencil_button.texture: "texture" = arcade.make_soft_circle_texture(65,
                                                                                 arcade.color.LIGHT_SLATE_GRAY,
                                                                                 outer_alpha=255)

    @classmethod
    def get_all_start_boards(cls) -> List[List[List[int]]]:
        """ getter for _ALL_START_BOARDS
        Args:
            None
        Returns:
            All sudoku game boards
        """
        return cls._ALL_START_BOARDS

    def get_rows(self) -> int:
        """ getter for _rows
        Args:
            None
        Returns:
            the amount of rows in the board
        """
        return self._rows

    def get_columns(self) -> int:
        """ getter for _columns
        Args:
            None
        Returns:
            the amount of columns in the board
        """
        return self._columns

    def get_start_board(self) -> List[List[int]]:
        """ getter for _start_board
        Args:
            None
        Returns:
            a randomized sudoku gameboard
        """
        return self._start_board

    def get_selected(self) -> Tuple[int, int]:
        """ getter for _selected
        Args:
            None
        Returns:
            The most recently clicked board coordinate
        """
        return self._selected

    def set_selected(self, cord: Tuple[int, int]) -> None:
        """ setter for _selected
        Args:
            cord: the newly selected coordinate
        Returns:
            None
        """
        self._selected = cord

    def set_board(self, board: List[List[int]]) -> None:
        """ setter for _board

        Args:
            board: sudoku game board where the user can input numbers
        Returns:
            None
        """
        self._board = board

    def set_number(self, coordinate: Tuple[int, int], value: int) -> None:
        """ setter for a coordinate in _board
        Args:
            coordinate: the coordinate that will have its value changed
            value: the value the coordinate will adopt
        Returns:
            None
        """
        self._board[coordinate[0]][coordinate[1]] = value

    def get_temp_board(self) -> Dict[Tuple, List]:
        """ getter for _temp_board
        Args:
            None
        Returns:
            the board containing temporary vaules
        """
        return self._temp_board

    def set_temp_board(self, temp_board: Dict[Tuple, List]) -> None:
        """ setter for _temp_board
        Args:
            temp_board: a game board containing temporary values
        Returns:
            None
        """
        self._temp_board = temp_board

    def set_temp_number(self, target: int, coordinate: Tuple[int, int]) -> None:
        """ setter for a coordinate in _temp_board given a number
        Args:
            target: the number that is to be added/removed
            coordinate: the coordinate in _temp_board that is changed
        Returns:
            None
        """
        present = False
        for i, num in enumerate(self._temp_board[coordinate]):
            if num == target:
                del self._temp_board[coordinate][i]
                present = True
        if not present:
            self._temp_board[coordinate].append(target)

    def set_temp_list(self, coordinate: Tuple[int, int], numbers: List[int]) -> None:
        """ setter for a coordinate in _temp_board given a list
        Args:
            coordinate: the coordinate in _temp_board that is to be changed
            numbers: a sorted list of numbers that the coordinate adopts
        Returns:
            None
        """
        self._temp_board[coordinate] = numbers

    def get_pencil_mode(self) -> bool:
        """ getter for _pencil_mode
        Args:
            None
        Returns:
            the status of pencil tool's activation
        """
        return self._pencil_mode

    def set_pencil_mode(self, value: bool) -> None:
        """ setter for _pencil_mode
        Args:
            value: toggle for pencil mode's activation
        Returns:
            None
        """
        self._pencil_mode = value

    def get_incorrect_coordinates(self) -> List[Tuple[int, int]]:
        """ getter for _incorrect_coordinates
        Args:
            None
        Returns:
            a list of coordinates containing the invalid inputted numbers
        """
        return self._incorrect_coordinates

    def set_incorrect_coordinates(self, value: List[Tuple[int, int]]) -> None:
        """ setter for _incorrect_coordinates
        Args:
            value: a list of coordinates containing invalid inputted numbers
        Returns:
            None
        """
        self._incorrect_coordinates = value

    def get_validate_button(self) -> "Sprite":
        """ getter for _validate_button
        Args:
            None
        Returns:
            a sprite that calls the validate function when pressed
        """
        return self._validate_button

    def get_solve_button(self) -> "Sprite":
        """ getter for _solve_button
        Args:
            None
        Returns:
            a sprite that calls the solve button when pressed
        """
        return self._solve_button

    def get_reset_button(self) -> "Sprite":
        """ getter for _reset_button
        Args:
            None
        Returns:
            a sprite that calls the reset button when pressed
        """
        return self._reset_button

    def get_pencil_button(self) -> "Sprite":
        """ getter for the _pencil_button
        Args:
            None
        Returns:
            a sprite that toggles pencil mode on/off when pressed
        """
        return self._pencil_button

    def set_pencil_button_texture(self, value: "Texture") -> None:
        """ setter for _pencil_button_texture
        Args:
            value: an arcade texture the pencil button sprite will adopt
        Returns:
            None
        """
        self._pencil_button.texture = value

    def reset_board(self) -> None:
        """ resets the board to its original state
        Args:
            None
        Returns:
            None
        """
        self._board = copy.deepcopy(self._start_board)
        self._temp_board = {(i, j): [] for i in range(9) for j in range(9)}
        self._incorrect_coordinates = []

    def find_empty(self) -> Union[Tuple[int, int], None]:
        """ finds the closest empty cell in the board
        Args:
            None
        Returns:
            The coordinate of the closest empty cell
        """
        for row in range(self._rows):
            for column in range(self._columns):
                if not self._board[row][column]:
                    return (row, column)
        return None

    def solve(self) -> bool:
        """ recursively solves the Sudoku board and indicates if not possible
        Args:
            None
        Returns:
            Whether or not the board is solvable
        """
        if not self.find_empty() and not self.get_invalid_numbers():
            return True
        else:
            coordinate = self.find_empty()
            row = coordinate[0]
            column = coordinate[1]

        for i in range(1, 10):
            self._board[row][column] = i
            result = self.get_invalid_numbers()
            if (row, column) in result:
                self._board[row][column] = 0
                continue

            if self.solve():
                return True

            self._board[row][column] = 0

        return False

    def get_invalid_numbers(self) -> Union[List[None], Set[Tuple[int, int]]]:
        """ cycles through each coordinate and ensures it abides Sudoku's rules
        Args:
            None
        Returns:
            a set of coordinates that do not follow Sudoku's rules
        """
        all_invalid_coordinates = []
        for column in range(self._columns):
            for row in range(self._rows):
                target = self._board[row][column]
                for y in range(self._rows):
                    if target == self._board[y][column] and row != y and self._board[y][column] != 0:
                        coordinate = (y, column)
                        all_invalid_coordinates.append(coordinate)

        for row in range(self._rows):
            for column in range(self._columns):
                target = self._board[row][column]
                for x in range(self._columns):
                    if target == self._board[row][x] and column != x and self._board[row][x] != 0:
                        coordinate = (row, x)
                        all_invalid_coordinates.append(coordinate)

        for row in range(self._rows):
            for column in range(self._columns):
                if not self._board[row][column]:
                    continue

                coordinate = (row, column)
                target = self._board[row][column]
                block_x = column // 3
                block_y = row // 3

                if block_x == 0:
                    start_x = 0
                    multiplier_x = 0
                elif block_x == 1:
                    start_x = 3
                    multiplier_x = 1
                else:
                    start_x = 6
                    multiplier_x = 2

                if block_y == 0:
                    start_y = 0
                    multiplier_y = 0
                elif block_y == 1:
                    start_y = 3
                    multiplier_y = 1
                else:
                    start_y = 6
                    multiplier_y = 2

                block = self._board[start_y:start_y+3]
                for y in range(len(block)):
                    new_row = block[y][start_x:start_x+3]
                    for x, number in enumerate(new_row):
                        number_coordinate_y = y + 3 * multiplier_y
                        number_coordinate_x = x + 3 * multiplier_x
                        number_coordinate = (number_coordinate_y, number_coordinate_x)
                        if number == target and number_coordinate != coordinate:
                            all_invalid_coordinates.append(coordinate)

        invalid_coordinates = []
        for coordinate in all_invalid_coordinates:
            y = coordinate[0]
            x = coordinate[1]
            if self._start_board[y][x] == 0:
                invalid_coordinates.append(coordinate)

        if not invalid_coordinates:
            return []

        return set(invalid_coordinates)

    def sort_numbers(self, numbers: List[int]) -> List[int]:
        """ takes a list of numbers and orderes them from least to greatest
        Args:
            numbers: a list of integers
        Returns:
            a sorted list of the numbers provided
        """
        if len(numbers) <= 1:
            return numbers

        mid = len(numbers) // 2
        l_side = self.sort_numbers(numbers[:mid])
        r_side = self.sort_numbers(numbers[mid:])
        sorted_list = []

        l_pointer = 0
        r_pointer = 0
        while l_pointer < len(l_side) and r_pointer < len(r_side):
            if l_side[l_pointer] < r_side[r_pointer]:
                sorted_list.append(l_side[l_pointer])
                l_pointer += 1
            else:
                sorted_list.append(r_side[r_pointer])
                r_pointer += 1

        while l_pointer < len(l_side):
            sorted_list.append(l_side[l_pointer])
            l_pointer += 1

        while r_pointer < len(r_side):
            sorted_list.append(r_side[r_pointer])
            r_pointer += 1

        return sorted_list

    def draw_temp_numbers(self) -> None:
        """ draws all the temporary numbers
        Args:
            None
        Returns:
            None
        """
        for y in range(self._rows):
            for x in range(self._columns):
                coordinate = (y, x)
                text = ' ' + ''.join(str(num)
                                     for num in self._temp_board[coordinate])
                translated_x = self._x_gap * (3/2) + ((self._x_gap) * (x - 1))
                translated_y = HEIGHT / (HEIGHT / 575) - ((HEIGHT / 12) * y)
                arcade.draw_text(text, translated_x, translated_y - 70,
                                 arcade.color.RED, font_size=10,
                                 font_name='arial', anchor_x="center")

    @staticmethod
    def draw_grid() -> None:
        """ draws the Sudoku game grid
        Args:
            None
        Returns:
            None
        """
        x_start = WIDTH / 9
        y_pos = HEIGHT / 6

        # HORIZONTAL LINES
        for i in range(1, 9):
            x_pos = x_start * i

            if i % 3 != 0:
                thickness = 1
                color = arcade.color.LIGHT_SLATE_GRAY
            else:
                thickness *= 3
                color = user.get_preferred_color()

            arcade.draw_rectangle_filled(x_pos, HEIGHT / 1.865,
                                         thickness, HEIGHT / (4/3),
                                         color)

        # VERTICAL LINES
        for i in range(1, 9):
            y_pos += (HEIGHT / (4/3)) / 9

            if i % 3 != 0:
                thickness = 1
                color = arcade.color.LIGHT_SLATE_GRAY
            else:
                thickness *= 3
                color = user.get_preferred_color()

            arcade.draw_rectangle_filled(WIDTH / 2, y_pos, thickness,
                                         WIDTH, color, tilt_angle=90)

    def draw_numbers(self) -> None:
        """ draws all inputted numbers
        Args:
            None
        Returns:
            None
        """
        for row in range(self._rows):
            for column in range(self._columns):
                if self._start_board[row][column]:
                    x = column
                    y = row
                    translated_x = self._x_gap * (3/2) + ((self._x_gap) * (x - 1))
                    translated_y = HEIGHT / (HEIGHT / 575) - ((HEIGHT / 12) * y)
                    arcade.draw_circle_filled(translated_x, translated_y - 51,
                                              17, arcade.color.PAYNE_GREY)
                    arcade.draw_text(str(self._start_board[row][column]),
                                     translated_x, translated_y - 60,
                                     arcade.color.LIGHT_GRAY, font_size=18,
                                     font_name='arial', anchor_x="center")
                elif self._board[row][column]:
                    x = column
                    y = row
                    translated_x = self._x_gap * (3/2) + ((self._x_gap) * (x - 1))
                    translated_y = HEIGHT / (HEIGHT / 575) - ((HEIGHT / 12) * y)

                    if self._selected == (column + 1, row + 1):
                        arcade.draw_text(str(self._board[row][column]),
                                         translated_x, translated_y - 60,
                                         arcade.color.BLACK, font_size=18,
                                         font_name='arial', anchor_x="center")
                    else:
                        arcade.draw_text(str(self._board[row][column]),
                                         translated_x,
                                         translated_y - 60,
                                         user.get_preferred_color(),
                                         font_size=18, font_name='arial',
                                         anchor_x="center")

    def draw_selected(self) -> None:
        """ draws the circle at the selected coordinate
        Args:
            None
        Returns:
            None
        """
        x = self._selected[0]
        y = self._selected[1]
        translated_x = self._x_gap / 2 + ((self._x_gap) * (x - 1))
        translated_y = HEIGHT / (HEIGHT / 575) - ((HEIGHT / 12) * y)
        arcade.draw_circle_filled(translated_x, translated_y - 1, 17,
                                  user.get_preferred_color())

    def draw_invalid_cord(self, coordinate: Tuple[int, int]) -> None:
        """ draws a red circle if the coordinate has an incorrect number
        Args:
            coordinate: the coordinate at which the indicator
                        will be drawn
        Returns:
            None
        """

        x = coordinate[1]
        y = coordinate[0]
        if self._board[y][x] == 0:
            return None
        translated_x = self._x_gap / 2 + ((self._x_gap) * (x - 1))
        translated_y = HEIGHT / (HEIGHT / 575) - ((HEIGHT / 12) * y)
        arcade.draw_circle_filled(translated_x + 88.88, translated_y - 51, 17,
                                  arcade.color.CADMIUM_RED)
        arcade.draw_text(str(self._board[y][x]), translated_x + 88.88,
                         translated_y - 60,
                         arcade.color.GHOST_WHITE, font_size=18,
                         font_name='arial', anchor_x="center")


class User:
    """ User class that personalizes the Sudoku game

    Attrs:
        _name(str): name of the user playing
        _preferred_color("color"): arcade color that the user prefers

    """
    def __init__(self, name: str, preferred_color: "color") -> None:
        """ Creates a user

        Args:
            name: name of the user playing
            preferred_color: arcade color that the user prefers
        """
        self._name = name
        self._preferred_color = preferred_color

    def get_name(self) -> str:
        """ getter for _name

        Args:
            None
        Returns:
            name of the user playing
        """
        return self._name

    def set_name(self, value: str) -> None:
        """ setter for _name

        Args:
            value: name of the user playing
        Returns:
            None
        """
        self._name = value

    def get_preferred_color(self) -> "color":
        """ getter for _preferred_color

        Args:
            None
        Returns:
            arcade color that the user prefers
        """
        return self._preferred_color

    def set_preferred_color(self, value: "color") -> None:
        """ setter for _preferred_color

        Args:
            value: arcade color that the user prefers
        Returns:
            None
        """
        self._preferred_color = value

    def draw_info(self, x: float, y: float, center: bool=False) -> None:
        """ Draws the name of the user in their favorite color

        Args:
            x: the x position the name will be drawn at
            y: the y position the name will be drawn at
            center: whether or not the name will be centered
        Returns:
            None
        """
        if center:
            arcade.draw_text(f"User: {self._name}", x, y,
                             self._preferred_color,
                             font_size=13, font_name='arial',
                             anchor_x='center')
        else:
            arcade.draw_text(f"User: {self._name}", x, y,
                             self._preferred_color,
                             font_size=13, font_name='arial')

    @staticmethod
    def draw_unpersonalized_name(x: float, y: float, center: bool=False) -> None:
        """ draws an unpersonalized name for users that did not input a name

        Args:
            x: the x position the name will be drawn at
            y: the y position the name will be drawn at
            center: whether or not the name will be centered
        Returns:
            None
        """
        if center:
            arcade.draw_text(f"User: Anon", x, y, arcade.color.WHITE,
                             font_size=13, font_name='arial',
                             anchor_x='center')
        else:
            arcade.draw_text("User: Anon", x, y, arcade.color.WHITE,
                             font_size=13, font_name='arial')


class Winner(User):
    """ Winner class

    Attributes:
        _all_winners(List["Winner"]): contains instances of Sudoku winners
        _name(str): the name of the winner
        _preferred_color("color"): the winner's preferred color
        _time(float): the time it took for the winner to complete the board

    """
    _all_winners = data

    def __init__(self, name: str, preferred_color: "color", time: float) -> None:
        """ Creates a winner

        Args:
            name: the name of the winner
            preferred_color: the winner's preferred_color
            time: the time it took for the winner to complete the board
        """
        super().__init__(name, preferred_color)
        self._time = time

    def get_time(self) -> float:
        """ getter for _time

        Args:
            None
        Returns:
            the time it took for the winner to complete the board
        """
        return self._time

    def set_time(self, value: float) -> None:
        """ setter for _time

        Args:
            the time it took for the winner to complete the board
        Returns:
            None
        """
        self._time = float(value)

    @classmethod
    def create_anon_winner(cls, color: "color", time: float) -> "Winner":
        """ creates winner without a given name
        Args:
            color: the winner's favorite color
            time: the time it took for the winner to complete the board
        Returns:
            a winner instance with 'Anonymous' as its name
        """
        return cls('Anonymous', color, time)

    @classmethod
    def sort_all_winner_times(cls) -> None:
        """ orders winners by the time it took them to complete the board

        Args:
            None
        Returns:
            None
        """
        sorted = False
        times_through = 0

        while not sorted:
            sorted = True
            for i in range(len(cls._all_winners) - 1 - times_through):
                if cls._all_winners[i]._time > cls._all_winners[i + 1]._time:
                    cls._all_winners[i], cls._all_winners[i + 1] = cls._all_winners[i + 1], cls._all_winners[i]
                    sorted = False
            times_through += 1

    @classmethod
    def draw_info(cls) -> None:
        """ draws the names and times of the top 10 quickest winners

        Args:
            None
        Returns:
            None
        """
        y_pos = 500
        i = 0
        for i in range(len(cls._all_winners)):
            if i > 9:
                break
            text = f"{i + 1}. {cls._all_winners[i]._name} - {cls._all_winners[i]._time}s"
            arcade.draw_text(text, WIDTH / 2, y_pos,
                             cls._all_winners[i]._preferred_color,
                             font_size=15, font_name='arial',
                             anchor_x="center")
            y_pos -= 50


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.play_button = arcade.Sprite(center_x=WIDTH / 2,
                                         center_y=500)
        self.play_button.texture = arcade.make_soft_square_texture(50,
                                                                   arcade.color.LIGHT_SLATE_GRAY,
                                                                   outer_alpha=255)
        self.instruction_button = arcade.Sprite(center_x=WIDTH / 2,
                                                center_y=350)
        self.instruction_button.texture = arcade.make_soft_square_texture(50,
                                                                          arcade.color.LIGHT_SLATE_GRAY,
                                                                          outer_alpha=255)
        self.leaderboard_button = arcade.Sprite(center_x=WIDTH / 2,
                                                center_y=200)
        self.leaderboard_button.texture = arcade.make_soft_square_texture(50,
                                                                          arcade.color.LIGHT_SLATE_GRAY,
                                                                          outer_alpha=255)
        self.quit_button = arcade.Sprite(center_x=50, center_y=550)
        self.quit_button.texture = arcade.make_soft_square_texture(50,
                                                                   arcade.color.LIGHT_SLATE_GRAY,
                                                                   outer_alpha=255)

    def on_show(self):
        arcade.set_background_color(arcade.color.EERIE_BLACK)

    def on_draw(self):
        arcade.start_render()
        if not user.get_name():
            user.draw_unpersonalized_name(WIDTH - 150, 575)
        else:
            user.draw_info(WIDTH - 150, 575)
        arcade.draw_text('SUDOKU', WIDTH / 2, 550,
                         user.get_preferred_color(),
                         font_size=30, font_name='arial',
                         anchor_x='center')
        self.play_button.draw()
        arcade.draw_text('P', WIDTH / 2, 485,
                         user.get_preferred_color(),
                         font_size=30, font_name='arial',
                         anchor_x='center')
        arcade.draw_text('LAY', WIDTH / 2 + 25, 485,
                         user.get_preferred_color(),
                         font_size=30, font_name='arial')
        self.instruction_button.draw()
        arcade.draw_text('I', WIDTH / 2, 335,
                         user.get_preferred_color(),
                         font_size=30, font_name='arial',
                         anchor_x='center')
        arcade.draw_text('NSTRUCTIONS', WIDTH / 2 + 25, 335,
                         user.get_preferred_color(),
                         font_size=30, font_name='arial')
        self.leaderboard_button.draw()
        arcade.draw_text('L', WIDTH / 2, 185,
                         user.get_preferred_color(),
                         font_size=30, font_name='arial',
                         anchor_x='center')
        arcade.draw_text('EADERBOARD', WIDTH / 2 + 25,
                         185, user.get_preferred_color(),
                         font_size=30, font_name='arial')
        self.quit_button.draw()
        arcade.draw_text('Q', 50, 535, user.get_preferred_color(),
                         font_size=30, font_name='arial',
                         anchor_x='center')
        arcade.draw_text('UIT', 50 + 55, 535, user.get_preferred_color(),
                         font_size=30, font_name='arial',
                         anchor_x='center')

    def on_mouse_press(self, x, y, button, modifiers):
        global game_view, game
        if self.play_button.collides_with_point([x, y]):
            game_view = MaxGameView()
            board_index = random.randrange(len(Sudoku.get_all_start_boards()))
            game = Sudoku(Sudoku.get_all_start_boards()[board_index])
            self.window.show_view(game_view)
        if self.instruction_button.collides_with_point([x, y]):
            instruction_view = InstructionView()
            self.window.show_view(instruction_view)
        if self.leaderboard_button.collides_with_point([x, y]):
            leaderboard_view = LeaderboardView()
            self.window.show_view(leaderboard_view)
        if self.quit_button.collides_with_point([x, y]):
            self.window.next_view()


class InstructionView(arcade.View):
    def __init__(self):
        super().__init__()
        with open('sudoku_instructions.txt', 'r', errors='ignore') as f:
            self.contents = f.read()

    def on_show(self):
        arcade.set_background_color(arcade.color.EERIE_BLACK)

    def on_key_press(self, symbol, modifiers):
        if symbol == 65307:
            try:
                self.window.show_view(menu_view)
            except:
                menu_view = MenuView()
                self.window.show_view(menu_view)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text(self.contents, WIDTH - 450,
                         200, user.get_preferred_color(),
                         font_size=13, font_name='arial', anchor_x='center')


class MaxGameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.seconds_elapsed = 0

    def on_show(self):
        arcade.set_background_color(arcade.color.EERIE_BLACK)

    def on_draw(self):
        self.timer = strftime("%H:%M:%S", gmtime(self.seconds_elapsed))
        arcade.start_render()
        arcade.draw_text(self.timer, WIDTH / 2, 565,
                         arcade.color.LIGHT_GRAY, font_size=18,
                         font_name='arial', anchor_x="center")

        game.draw_selected()
        if not user.get_name():
            user.draw_unpersonalized_name(WIDTH / 2,
                                          550, True)
        else:
            user.draw_info(WIDTH / 2, 550, True)
        if game.get_incorrect_coordinates():
            for coordinate in game.get_incorrect_coordinates():
                game.draw_invalid_cord(coordinate)
        game.draw_grid()
        game.draw_numbers()
        game.draw_temp_numbers()

        game.get_validate_button().draw()
        game.get_solve_button().draw()
        game.get_reset_button().draw()
        game.get_pencil_button().draw()

        arcade.draw_text('V', 133.33, 30,
                         user.get_preferred_color(), font_size=40,
                         font_name='arial', anchor_x="center")
        arcade.draw_text('P', 400, 30,
                         user.get_preferred_color(), font_size=40,
                         font_name='arial', anchor_x="center")
        arcade.draw_text('S', 666.66, 30,
                         user.get_preferred_color(), font_size=40,
                         font_name='arial', anchor_x="center")
        arcade.draw_text('R', 750, 565,
                         user.get_preferred_color(), font_size=20,
                         font_name='arial', anchor_x="center")

    def on_key_press(self, symbol, modifiers):
        x = game.get_selected()[0] - 1
        y = game.get_selected()[1] - 1
        coordinate = (y, x)

        if not game.get_pencil_mode():
            if game.get_temp_board()[(y, x)]:
                numbers = []
                game.set_temp_list((y, x), numbers)
            if game.get_start_board()[y][x]:
                pass
            elif symbol == 49:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 1)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                else:
                    game.set_number(coordinate, 1)
            elif symbol == 50:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 2)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                else:
                    game.set_number(coordinate, 2)
            elif symbol == 51:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 3)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                else:
                    game.set_number(coordinate, 3)
            elif symbol == 52:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 4)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                else:
                    game.set_number(coordinate, 4)
            elif symbol == 53:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 5)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                else:
                    game.set_number(coordinate, 5)
            elif symbol == 54:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 6)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                else:
                    game.set_number(coordinate, 6)
            elif symbol == 55:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 7)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                else:
                    game.set_number(coordinate, 7)
            elif symbol == 56:

                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 8)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                else:
                    game.set_number(coordinate, 8)
            elif symbol == 57:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 9)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                else:
                    game.set_number(coordinate, 9)
            elif symbol == 65288 or symbol == 48:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 0)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                else:
                    game.set_number(coordinate, 0)
            else:
                pass

        if game.get_pencil_mode():
            if game.get_start_board()[y][x]:
                pass
            elif symbol == 49:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 0)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                    game.set_temp_number(1, coordinate)
                else:
                    game.set_number(coordinate, 0)
                    game.set_temp_number(1, coordinate)
            elif symbol == 50:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 0)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                    game.set_temp_number(2, coordinate)
                else:
                    game.set_number(coordinate, 0)
                    game.set_temp_number(2, coordinate)
            elif symbol == 51:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 0)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                    game.set_temp_number(3, coordinate)
                else:
                    game.set_number(coordinate, 0)
                    game.set_temp_number(3, coordinate)
            elif symbol == 52:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 0)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                    game.set_temp_number(4, coordinate)
                else:
                    game.set_number(coordinate, 0)
                    game.set_temp_number(4, coordinate)
            elif symbol == 53:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 0)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                    game.set_temp_number(5, coordinate)
                else:
                    game.set_number(coordinate, 0)
                    game.set_temp_number(5, coordinate)
            elif symbol == 54:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 0)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                    game.set_temp_number(6, coordinate)
                else:
                    game.set_number(coordinate, 0)
                    game.set_temp_number(6, coordinate)
            elif symbol == 55:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 0)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                    game.set_temp_number(7, coordinate)
                else:
                    game.set_number(coordinate, 0)
                    game.set_temp_number(7, coordinate)
            elif symbol == 56:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 0)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                    game.set_temp_number(8, coordinate)
                else:
                    game.set_number(coordinate, 0)
                    game.set_temp_number(8, coordinate)
            elif symbol == 57:
                if coordinate in game.get_incorrect_coordinates():
                    game.set_number(coordinate, 0)
                    new_board = game.get_incorrect_coordinates()
                    new_board.remove(coordinate)
                    game.set_incorrect_coordinates(new_board)
                    game.set_temp_number(9, coordinate)
                else:
                    game.set_number(coordinate, 0)
                    game.set_temp_number(9, coordinate)
            else:
                pass
            for y in range(game.get_rows()):
                for x in range(game.get_columns()):
                    coordinate = (y, x)
                    numbers = game.get_temp_board()[coordinate]
                    ordered_numbers = game.sort_numbers(numbers)
                    game.set_temp_list(coordinate, ordered_numbers)

        if symbol == 65307:
            pause_screen = PauseScreen(self)
            self.window.show_view(pause_screen)
        else:
            pass

    def on_update(self, delta_time):
        self.seconds_elapsed += delta_time

    def on_mouse_press(self, x, y, button, modifiers):
        global winner
        x_coordinate = math.ceil(x / (WIDTH / 9))
        y_coordinate = 11 - math.ceil((y - (HEIGHT / 12)) / (HEIGHT / 12))
        if x_coordinate <= 9 and y_coordinate <= 9 and x_coordinate > 0 and y_coordinate > 0:
            coordinate = (x_coordinate, y_coordinate)
            game.set_selected(coordinate)

        if game.get_validate_button().collides_with_point([x, y]):
            incorrect_coordinates = game.get_invalid_numbers()
            game.set_incorrect_coordinates(incorrect_coordinates)
            if not game.get_incorrect_coordinates() and not game.find_empty():
                if not user.get_name():
                    winner = Winner.create_anon_winner(user.get_preferred_color(),
                                                       round(self.seconds_elapsed, 1))
                else:
                    winner = Winner(user.get_name(),
                                    user.get_preferred_color(),
                                    round(self.seconds_elapsed, 1))

                data.append(winner)
                save_data()
                win_view = WinView(self.seconds_elapsed)
                self.window.show_view(win_view)

        if game.get_solve_button().collides_with_point([x, y]):
            game.set_board(copy.deepcopy(game.get_start_board()))
            game.set_incorrect_coordinates([])
            game.solve()
            temp_board = {(i, j): [] for i in range(9) for j in range(9)}
            game.set_temp_board(temp_board)

        if game.get_reset_button().collides_with_point([x, y]):
            game.reset_board()

        if game.get_pencil_button().collides_with_point([x, y]):
            if game.get_pencil_mode():
                game.set_pencil_mode(False)
                texture = arcade.make_soft_circle_texture(65,
                                                          arcade.color.LIGHT_SLATE_GRAY,
                                                          outer_alpha=255)
                game.set_pencil_button_texture(texture)
            else:
                game.set_pencil_mode(True)
                texture = arcade.make_soft_circle_texture(65,
                                                          arcade.color.BOSTON_UNIVERSITY_RED,
                                                          outer_alpha=255)
                game.set_pencil_button_texture(texture)


class PauseScreen(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

    def on_show(self):
        arcade.set_background_color(arcade.color.EERIE_BLACK)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text('>PRESS <ESCAPE> TO GIVE UP',
                         WIDTH / 2, HEIGHT / 2,
                         arcade.color.LIGHT_GRAY, font_size=25,
                         font_name='arial', anchor_x="center")
        arcade.draw_text('>PRESS <ENTER> TO RESUME GAME',
                         WIDTH / 2, HEIGHT / 1.5,
                         arcade.color.LIGHT_GRAY, font_size=25,
                         font_name='arial', anchor_x="center")
        arcade.draw_text('>PRESS <M> TO RETURN TO THE MENU',
                         WIDTH / 2, HEIGHT / 3,
                         arcade.color.LIGHT_GRAY, font_size=25,
                         font_name='arial', anchor_x="center")

    def on_key_press(self, symbol, modifiers):
        if symbol == 65307:
            self.window.next_view()
        elif symbol == 65293:
            self.window.show_view(self.game_view)
        elif symbol == 109:
            try:
                self.window.show_view(menu_view)
            except:
                menu_view = MenuView()
                self.window.show_view(menu_view)
        else:
            pass


class IntroductionView(arcade.View):
    def __init__(self):
        super().__init__()
        self.text = 'USERNAME: '
        self.preferred_color = None
        self.green_button = arcade.Sprite(center_x=WIDTH / 2,
                                          center_y=500)
        self.green_button.texture = arcade.make_soft_square_texture(50,
                                                                    arcade.color.GREEN_YELLOW,
                                                                    outer_alpha=255)
        self.blue_button = arcade.Sprite(center_x=WIDTH / 2,
                                         center_y=350)
        self.blue_button.texture = arcade.make_soft_square_texture(50,
                                                                   arcade.color.BLIZZARD_BLUE,
                                                                   outer_alpha=255)
        self.white_button = arcade.Sprite(center_x=WIDTH / 2,
                                          center_y=200)
        self.white_button.texture = arcade.make_soft_square_texture(50,
                                                                    arcade.color.WHITE,
                                                                    outer_alpha=255)

    def on_show(self):
        arcade.set_background_color(arcade.color.EERIE_BLACK)

    def on_draw(self):
        arcade.start_render()
        if not self.preferred_color:
            arcade.draw_text('CLICK YOUR PREFERRED COLOR', WIDTH / 2,
                             HEIGHT - 50,
                             arcade.color.LIGHT_GRAY, font_size=15,
                             font_name='arial', anchor_x="center")
            self.green_button.draw()
            self.blue_button.draw()
            self.white_button.draw()
        else:
            arcade.draw_text(self.text, WIDTH / 2,
                             HEIGHT / 2, arcade.color.BLIZZARD_BLUE,
                             font_size=25, anchor_x='center')
            arcade.draw_text("""TYPE IN YOUR USERNAME AND
                             PRESS <ENTER> TO CONTINUE""",
                             WIDTH / 2, HEIGHT - 50,
                             arcade.color.LIGHT_GRAY, font_size=15,
                             font_name='arial', anchor_x="center")

    def on_key_press(self, symbol, modifiers):
        global user
        if self.preferred_color:
            if symbol == 65288 and len(self.text) > 1:
                self.text = self.text[:10]
            elif translate_symbol(symbol) is not None and len(self.text) <= 18:
                self.text += translate_symbol(symbol)
            else:
                pass

            if symbol == 65293:
                name = self.text[10:]
                user = User(name, self.preferred_color)
                menu_view = MenuView()
                self.window.show_view(menu_view)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.green_button.collides_with_point([x, y]):
            self.preferred_color = arcade.color.GREEN_YELLOW
        if self.blue_button.collides_with_point([x, y]):
            self.preferred_color = arcade.color.BLIZZARD_BLUE
        if self.white_button.collides_with_point([x, y]):
            self.preferred_color = arcade.color.WHITE


class LeaderboardView(arcade.View):
    def __init__(self):
        super().__init__()

    def on_show(self):
        arcade.set_background_color(arcade.color.EERIE_BLACK)
        Winner._all_winners = data
        Winner.sort_all_winner_times()

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text('>PRESS <M> TO RETURN TO MENU', WIDTH / 2,
                         HEIGHT - 50,
                         arcade.color.LIGHT_GRAY, font_size=25,
                         font_name='arial', anchor_x="center")
        Winner.draw_info()

    def on_key_press(self, symbol, modifiers):
        if symbol == 109:
            try:
                self.window.show_view(menu_view)
            except:
                menu_view = MenuView()
                self.window.show_view(menu_view)


class WinView(arcade.View):
    def __init__(self, time):
        super().__init__()
        self.time = round(time, 1)

    def on_show(self):
        arcade.set_background_color(arcade.color.EERIE_BLACK)

    def on_draw(self):
        arcade.start_render()
        if not user.get_name():
            text = f"""Congratulation on winning, Anonymous!
            You completed this board with a time of: {self.time}"""
        else:
            text = f"""Congratulation on winning, {user.get_name()}!
            You completed this board with a time of: {self.time}"""
        arcade.draw_text(text, WIDTH / 2, HEIGHT / 2,
                         user.get_preferred_color(), font_size=15,
                         font_name='arial', anchor_x="center")
        arcade.draw_text('To return to the menu, press <M>',
                         WIDTH / 2, HEIGHT / 1.5,
                         user.get_preferred_color(),
                         font_size=15, font_name='arial',
                         anchor_x="center")
        arcade.draw_text('To see the leaderboard, press <L>',
                         WIDTH / 2, HEIGHT / 3,
                         user.get_preferred_color(),
                         font_size=15, font_name='arial', anchor_x="center")

    def on_key_press(self, symbol, modifiers):
        if symbol == 109:
            global game, game_view
            del game
            del game_view
            try:
                self.window.show_view(menu_view)
            except:
                menu_view = MenuView()
                self.window.show_view(menu_view)
        if symbol == 108:
            board_index = random.randrange(len(Sudoku.get_all_start_boards()))
            leaderboard = LeaderboardView()
            self.window.show_view(leaderboard)


if __name__ == "__main__":
    """This section of code will allow you to run your View
    independently from the main.py file and its Director.

    You can ignore this whole section. Keep it at the bottom
    of your code.

    It is advised you do not modify it unless you really know
    what you are doing.
    """
    from utils import FakeDirector
    load_data()
    window = arcade.Window(WIDTH, HEIGHT)
    introduction_view = IntroductionView()
    menu_view = MenuView()
    window.show_view(introduction_view)
    arcade.run()
