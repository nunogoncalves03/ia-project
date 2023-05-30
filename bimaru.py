# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 56:
# 102802 Fabio Mata
# 103392 Nuno Goncalves

import sys
from search import Problem, Node, depth_first_tree_search
from typing import List, TypeVar, Tuple

Board = TypeVar("Board", bound="Board")


class BimaruState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id


class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    ROWS_NUMBER = 10
    COLUMNS_NUMBER = 10
    OUT_OF_BOUNDS = "x"
    HORIZONTAL_DIRECTION = 0
    VERTICAL_DIRECTION = 1

    def __init__(
        self,
        row_hints: List[int],
        column_hints: List[int],
        board: List[List[str]],
        boats: List[int],
        empty_cells: int,
    ):
        self.board = [[item for item in row] for row in board]
        self.row_hints = [item for item in row_hints]
        self.column_hints = [item for item in column_hints]
        self.boats = [count for count in boats]
        self.is_valid = True
        self.empty_cells = empty_cells

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""

        if row >= 0 and row <= Board.ROWS_NUMBER - 1:
            if col >= 0 and col <= Board.COLUMNS_NUMBER - 1:
                return self.board[row][col]

        return Board.OUT_OF_BOUNDS

    def place_symbol(self, symbol: str, row: int, col: int):
        """Places the given symbol in the given position if valid,
        does nothing otherwise."""

        if row >= 0 and row <= Board.ROWS_NUMBER - 1:
            if col >= 0 and col <= Board.COLUMNS_NUMBER - 1:
                prev_symbol = self.get_value(row, col)
                if prev_symbol != symbol.upper():
                    if prev_symbol == "":
                        self.empty_cells -= 1

                    if prev_symbol not in ("$", "m") and symbol not in ("w", "W"):
                        self.row_hints[row] -= 1
                        self.column_hints[col] -= 1

                    self.board[row][col] = symbol

    def adjacent_vertical_values(self, row: int, col: int) -> Tuple[str, str]:
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""

        return (self.get_value(row - 1, col), self.get_value(row + 1, col))

    def adjacent_horizontal_values(self, row: int, col: int) -> Tuple[str, str]:
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""

        return (self.get_value(row, col - 1), self.get_value(row, col + 1))

    def adjacent_diagonal_values(self, row: int, col: int) -> Tuple[str, str, str, str]:
        """Devolve os valores em cima à esquerda,
        em cima à direita, em baixo à direita e em baixo à esquerda,
        respectivamente."""

        return (
            self.get_value(row - 1, col - 1),
            self.get_value(row - 1, col + 1),
            self.get_value(row + 1, col + 1),
            self.get_value(row + 1, col - 1),
        )

    def get_boats_row(self, row) -> int:
        """Returns the number of boat cells in a row"""

        count = 0
        for col in range(Board.COLUMNS_NUMBER):
            if self.get_value(row, col) not in ("", "w", "W", Board.OUT_OF_BOUNDS):
                count += 1

        return count

    def get_boats_col(self, col) -> int:
        """Returns the number of boat cells in a column"""

        count = 0
        for row in range(Board.ROWS_NUMBER):
            if self.get_value(row, col) not in ("", "w", "W", Board.OUT_OF_BOUNDS):
                count += 1

        return count

    def is_goal(self) -> bool:
        """Returns True if the board is solved"""

        hints = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        return (
            self.empty_cells == 0
            and self.boats == [0, 0, 0, 0]
            and self.row_hints == hints
            and self.column_hints == hints
        )

    def process_cell(self, row: int, col: int):
        """Places water and $ around the given cell
        accordingly to the symbol it holds."""

        symbol = self.board[row][col]

        if symbol in ("C", "c"):
            self.process_C(row, col)
        elif symbol in ("M", "m"):
            self.process_M(row, col)
        elif symbol in ("T", "t", "B", "b"):
            self.process_T_B(symbol, row, col)
        elif symbol in ("L", "l", "R", "r"):
            self.process_L_R(symbol, row, col)
        elif symbol == "$":
            self.process_placeholder(row, col)

    def process_T_B(self, symbol: str, row: int, col: int):
        """Places water and placeholders around T and B cells if possible"""

        # upper row
        self.place_symbol("w", row - 1, col - 1)
        # only cover the cell above the symbol if it's T
        if symbol in ("T", "t"):
            self.place_symbol("w", row - 1, col)
        elif self.get_value(row - 1, col) == "":
            self.place_symbol("$", row - 1, col)
        self.place_symbol("w", row - 1, col + 1)

        # only cover the further side cells above the symbol if it's B
        if symbol in ("B", "b"):
            self.place_symbol("w", row - 2, col - 1)
            self.place_symbol("w", row - 2, col + 1)

        # to the left
        self.place_symbol("w", row, col - 1)

        # to the right
        self.place_symbol("w", row, col + 1)

        # inferior row
        self.place_symbol("w", row + 1, col - 1)
        # only cover the cell underneath the symbol if it's B
        if symbol in ("B", "b"):
            self.place_symbol("w", row + 1, col)
        elif self.get_value(row + 1, col) == "":
            self.place_symbol("$", row + 1, col)
        self.place_symbol("w", row + 1, col + 1)

        # only cover the further side cells underneath the symbol if it's T
        if symbol in ("T", "t"):
            self.place_symbol("w", row + 2, col - 1)
            self.place_symbol("w", row + 2, col + 1)

    def process_L_R(self, symbol: str, row: int, col: int):
        """Places water and placeholders around L and R cells if possible"""

        # upper row
        # only cover the further left side cell above the symbol if it's R
        if symbol in ("R", "r"):
            self.place_symbol("w", row - 1, col - 2)
        self.place_symbol("w", row - 1, col - 1)
        self.place_symbol("w", row - 1, col)
        self.place_symbol("w", row - 1, col + 1)
        # only cover the further right side cell above the symbol if it's L
        if symbol in ("L", "l"):
            self.place_symbol("w", row - 1, col + 2)

        # to the right
        if symbol in ("R", "r"):
            self.place_symbol("w", row, col + 1)
        elif self.get_value(row, col + 1) == "":
            self.place_symbol("$", row, col + 1)

        # to the left
        if symbol in ("L", "l"):
            self.place_symbol("w", row, col - 1)
        elif self.get_value(row, col - 1) == "":
            self.place_symbol("$", row, col - 1)

        # inferior row
        # only cover the further left side cell underneath the symbol if it's R
        if symbol in ("R", "r"):
            self.place_symbol("w", row + 1, col - 2)
        self.place_symbol("w", row + 1, col - 1)
        self.place_symbol("w", row + 1, col)
        self.place_symbol("w", row + 1, col + 1)
        # only cover the further right side cell underneath the symbol if it's L
        if symbol in ("L", "l"):
            self.place_symbol("w", row + 1, col + 2)

    def process_C(self, row: int, col: int):
        """Places water and placeholders around C cells if possible"""

        # upper row
        self.place_symbol("w", row - 1, col - 1)
        self.place_symbol("w", row - 1, col)
        self.place_symbol("w", row - 1, col + 1)
        # to the left
        self.place_symbol("w", row, col - 1)
        # to the right
        self.place_symbol("w", row, col + 1)
        # inferior row
        self.place_symbol("w", row + 1, col - 1)
        self.place_symbol("w", row + 1, col)
        self.place_symbol("w", row + 1, col + 1)

    def process_M(self, row: int, col: int):
        """Places water and placeholders around M cells if possible"""

        vertical_adj_values = self.adjacent_vertical_values(row, col)
        horizontal_adj_values = self.adjacent_horizontal_values(row, col)

        # place water diagonally
        self.place_symbol("w", row - 1, col - 1)
        self.place_symbol("w", row - 1, col + 1)
        self.place_symbol("w", row + 1, col + 1)
        self.place_symbol("w", row + 1, col - 1)

        # check if M is part of a horizontally displayed ship
        if (
            "W" in vertical_adj_values
            or "w" in vertical_adj_values
            or row == Board.ROWS_NUMBER - 1
            or row == 0
            or any(
                map(
                    lambda x: x not in ("", "W", "w", Board.OUT_OF_BOUNDS),
                    horizontal_adj_values,
                )
            )
        ):
            if horizontal_adj_values[0] == "":
                self.place_symbol("$", row, col - 1)
            if horizontal_adj_values[1] == "":
                self.place_symbol("$", row, col + 1)
            for i in (row - 1, row + 1):
                for j in (col - 2, col - 1, col, col + 1, col + 2):
                    self.place_symbol("w", i, j)
        # check if M is part of a vertically displayed ship
        elif (
            "W" in horizontal_adj_values
            or "w" in horizontal_adj_values
            or col == Board.COLUMNS_NUMBER - 1
            or col == 0
            or any(
                map(
                    lambda x: x not in ("", "W", "w", Board.OUT_OF_BOUNDS),
                    vertical_adj_values,
                )
            )
        ):
            if vertical_adj_values[0] == "":
                self.place_symbol("$", row - 1, col)
            if vertical_adj_values[1] == "":
                self.place_symbol("$", row + 1, col)
            for i in (row - 2, row - 1, row, row + 1, row + 2):
                for j in (col - 1, col + 1):
                    self.place_symbol("w", i, j)

    def process_placeholder(self, row: int, col: int):
        """Places water around placeholder cells if possible"""

        # diagonals
        self.place_symbol("w", row - 1, col - 1)
        self.place_symbol("w", row - 1, col + 1)
        self.place_symbol("w", row + 1, col + 1)
        self.place_symbol("w", row + 1, col - 1)

    def place_water_row(self, row: int):
        """Fills empty cells of a row with water if possible"""

        if self.row_hints[row] == 0:
            for col in range(Board.COLUMNS_NUMBER):
                if self.board[row][col] == "":
                    self.place_symbol("w", row, col)

    def place_water_column(self, col: int):
        """Fills empty cells of a column with water if possible"""

        if self.column_hints[col] == 0:
            for row in range(Board.ROWS_NUMBER):
                if self.board[row][col] == "":
                    self.place_symbol("w", row, col)

    def place_boats_row(self, row: int):
        """Fills empty cells of a row with placeholders if possible"""

        empty_counter = 0
        for col in range(Board.COLUMNS_NUMBER):
            if self.board[row][col] == "":
                empty_counter += 1

        if empty_counter == self.row_hints[row]:
            for col in range(Board.COLUMNS_NUMBER):
                if self.board[row][col] == "":
                    self.place_symbol("$", row, col)

    def place_boats_column(self, col: int):
        """Fills empty cells of a column with placeholders if possible"""

        empty_counter = 0
        for row in range(Board.ROWS_NUMBER):
            if self.board[row][col] == "":
                empty_counter += 1

        if empty_counter == self.column_hints[col]:
            for row in range(Board.ROWS_NUMBER):
                if self.board[row][col] == "":
                    self.place_symbol("$", row, col)

    def place_boat(self, row: int, col: int, size: int, direction: int) -> Board:
        """Receives an action and places a boat with the given size and direction on the position (row, col)"""

        new_board = Board(
            self.row_hints, self.column_hints, self.board, self.boats, self.empty_cells
        )

        if size == 1:
            new_board.place_symbol("c", row, col)

            new_board.boats[size - 1] -= 1
            new_board.cleanup()
            return new_board

        for i in range(0, size):
            if direction == Board.HORIZONTAL_DIRECTION:
                if i == 0:
                    new_board.place_symbol("l", row, col)
                elif i == size - 1:
                    new_board.place_symbol("r", row, col)
                else:
                    new_board.place_symbol("m", row, col)

                col += 1

            elif direction == Board.VERTICAL_DIRECTION:
                if i == 0:
                    new_board.place_symbol("t", row, col)
                elif i == size - 1:
                    new_board.place_symbol("b", row, col)
                else:
                    new_board.place_symbol("m", row, col)

                row += 1

        new_board.boats[size - 1] -= 1
        new_board.cleanup()
        return new_board

    def calculate_placeable_boats(self) -> List[Tuple[int, int, int, int, int]]:
        """Calculates all possible actions"""

        if not self.is_valid:
            return []

        placeable_boats = []
        size = 4

        while size > 0 and self.boats[size - 1] == 0:
            size -= 1

        if size == 0:
            return []

        possible_circles = []

        # horizontal
        for row in range(Board.ROWS_NUMBER):
            total_boats = self.get_boats_row(row)

            if size - total_boats > self.row_hints[row]:
                continue

            for col in range(Board.COLUMNS_NUMBER):
                override_count = 0

                if self.get_value(row, col) in (
                    "",
                    "$",
                    "L",
                ) and self.get_value(
                    row, col - 1
                ) not in ("$", "L", "M"):
                    if self.get_value(row, col) != "":
                        override_count += 1

                    i = 1
                    while i < size and self.get_value(row, col + i) in (
                        "",
                        "$",
                        "M",
                    ):
                        if self.get_value(row, col + i) != "":
                            override_count += 1

                        i += 1

                    if (
                        i == size - 1
                        and self.get_value(row, col + i) == "R"
                        and size - 1 - override_count <= self.row_hints[row]
                    ):
                        placeable_boats.append(
                            (
                                row,
                                col,
                                size,
                                Board.HORIZONTAL_DIRECTION,
                                self.row_hints[row] - (size - 1 - override_count),
                            )
                        )

                    if (
                        i == size
                        and self.get_value(row, col + i)
                        in ("", "w", "W", Board.OUT_OF_BOUNDS)
                        and self.get_value(row, col + i + 1) != "R"
                        and size - override_count <= self.row_hints[row]
                    ):
                        if size == 1 and self.get_value(row, col) in ("", "$"):
                            possible_circles.append((row, col))
                        elif size != 1 and self.get_value(row, col + i - 1) in (
                            "",
                            "$",
                            "R",
                        ):
                            placeable_boats.append(
                                (
                                    row,
                                    col,
                                    size,
                                    Board.HORIZONTAL_DIRECTION,
                                    self.row_hints[row] - (size - override_count),
                                )
                            )

        # vertical
        for col in range(Board.COLUMNS_NUMBER):
            total_boats = self.get_boats_col(col)

            if size - total_boats > self.column_hints[col]:
                continue

            for row in range(Board.ROWS_NUMBER):
                override_count = 0

                if self.get_value(row, col) in (
                    "",
                    "$",
                    "T",
                ) and self.get_value(
                    row - 1, col
                ) not in ("$", "T", "M"):
                    if self.get_value(row, col) != "":
                        override_count += 1

                    i = 1
                    while i < size and self.get_value(row + i, col) in (
                        "",
                        "$",
                        "M",
                    ):
                        if self.get_value(row + i, col) != "":
                            override_count += 1

                        i += 1

                    if (
                        i == size - 1
                        and self.get_value(row + i, col) == "B"
                        and size - 1 - override_count <= self.column_hints[col]
                    ):
                        placeable_boats.append(
                            (
                                row,
                                col,
                                size,
                                Board.VERTICAL_DIRECTION,
                                self.column_hints[col] - (size - 1 - override_count),
                            )
                        )

                    if (
                        i == size
                        and self.get_value(row + i, col)
                        in ("", "w", "W", Board.OUT_OF_BOUNDS)
                        and self.get_value(row + i + 1, col) != "B"
                        and size - override_count <= self.column_hints[col]
                    ):
                        if size == 1 and self.get_value(row, col) in ("", "$"):
                            if (row, col) in possible_circles:
                                placeable_boats.append(
                                    (
                                        row,
                                        col,
                                        size,
                                        Board.VERTICAL_DIRECTION,
                                        self.column_hints[col]
                                        - (size - override_count),
                                    )
                                )
                        elif size != 1 and self.get_value(row + i - 1, col) in (
                            "",
                            "$",
                            "B",
                        ):
                            placeable_boats.append(
                                (
                                    row,
                                    col,
                                    size,
                                    Board.VERTICAL_DIRECTION,
                                    self.column_hints[col] - (size - override_count),
                                )
                            )

        return sorted(placeable_boats, key=lambda action: action[4])

    def replace_placeholders(self):
        """Replaces placeholders with the respective boat if possible"""

        for row in range(Board.ROWS_NUMBER):
            for col in range(Board.COLUMNS_NUMBER):
                if self.get_value(row, col) == "$":
                    if self.adjacent_horizontal_values(row, col)[0] == "L" or (
                        self.adjacent_horizontal_values(row, col)[1]
                        not in ("", "w", "W", Board.OUT_OF_BOUNDS)
                        and self.adjacent_horizontal_values(row, col)[0]
                        not in ("", "$", "M")
                    ):
                        size = 0
                        i = 1
                        while self.get_value(row, col + i) in ("$", "m", "M"):
                            i += 1

                        if self.get_value(row, col + i) in (
                            "w",
                            "W",
                            Board.OUT_OF_BOUNDS,
                        ):
                            self.place_symbol("r", row, col + i - 1)
                            i -= 1

                        if self.get_value(row, col + i) in ("r", "R"):
                            size = 1
                            while self.get_value(row, col + i - 1) in ("$", "m", "M"):
                                self.place_symbol("m", row, col + i - 1)
                                i -= 1
                                size += 1

                            if self.get_value(row, col + i - 1) != "L":
                                self.place_symbol("l", row, col + i)
                            elif self.get_value(row, col + i - 1) == "L":
                                size += 1

                        if size > 1 and size < 5:
                            if self.boats[size - 1] == 0:
                                self.is_valid = False
                            else:
                                self.boats[size - 1] -= 1
                        elif size >= 5:
                            self.is_valid = False

                    elif self.adjacent_vertical_values(row, col)[0] == "T" or (
                        self.adjacent_vertical_values(row, col)[1]
                        not in ("", "w", "W", Board.OUT_OF_BOUNDS)
                        and self.adjacent_vertical_values(row, col)[0]
                        not in ("", "$", "M")
                    ):
                        size = 0
                        i = 1
                        while self.get_value(row + i, col) in ("$", "m", "M"):
                            i += 1

                        if self.get_value(row + i, col) in (
                            "w",
                            "W",
                            Board.OUT_OF_BOUNDS,
                        ):
                            self.place_symbol("b", row + i - 1, col)
                            i -= 1

                        if self.get_value(row + i, col) in ("b", "B"):
                            size = 1
                            while self.get_value(row + i - 1, col) in (
                                "$",
                                "m",
                                "M",
                            ):
                                self.place_symbol("m", row + i - 1, col)
                                i -= 1
                                size += 1

                            if self.get_value(row + i - 1, col) != "T":
                                self.place_symbol("t", row + i, col)
                            elif self.get_value(row + i - 1, col) == "T":
                                size += 1

                        if size > 0 and size < 5:
                            if self.boats[size - 1] == 0:
                                self.is_valid = False
                            else:
                                self.boats[size - 1] -= 1
                        elif size >= 5:
                            self.is_valid = False

                    elif (
                        all(
                            value in ("w", "W", Board.OUT_OF_BOUNDS)
                            for value in self.adjacent_horizontal_values(row, col)
                        )
                        and all(
                            value in ("w", "W", Board.OUT_OF_BOUNDS)
                            for value in self.adjacent_vertical_values(row, col)
                        )
                        and all(
                            value in ("w", "W", Board.OUT_OF_BOUNDS)
                            for value in self.adjacent_diagonal_values(row, col)
                        )
                    ):
                        self.place_symbol("c", row, col)
                        if self.boats[0] == 0:
                            self.is_valid = False
                        else:
                            self.boats[0] -= 1

    def cleanup(self):
        """Places water, placeholders and replaces placeholders if possible"""

        while True:
            empty_cells = self.empty_cells

            for i in range(Board.ROWS_NUMBER):
                for j in range(Board.COLUMNS_NUMBER):
                    self.process_cell(i, j)

            for i in range(Board.ROWS_NUMBER):
                self.place_water_row(i)
                self.place_water_column(i)
                self.place_boats_row(i)
                self.place_boats_column(i)

            self.replace_placeholders()

            for i in range(Board.ROWS_NUMBER):
                self.place_water_row(i)
                self.place_water_column(i)
                self.place_boats_row(i)
                self.place_boats_column(i)

            for i in range(Board.ROWS_NUMBER):
                for j in range(Board.COLUMNS_NUMBER):
                    self.process_cell(i, j)

            if empty_cells == self.empty_cells:
                break

    def __str__(self):
        """Returns a string representation of the Board as described in
        topic 4.2 of the statement."""

        string = ""

        for row in self.board:
            for symbol in row:
                if symbol == "":
                    symbol = " "
                elif symbol == "w":
                    symbol = "."
                string += symbol
            string += "\n"

        return string

    @staticmethod
    def parse_instance() -> Board:
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board."""

        row_hints = sys.stdin.readline().split("\t")[1:]  # ignore ROW keyword
        row_hints = [int(x) for x in row_hints]

        column_hints = sys.stdin.readline().split("\t")[1:]  # ignore COLUMN keyword
        column_hints = [int(x) for x in column_hints]

        hints_number = int(sys.stdin.readline())

        board = [
            ["" for _ in range(Board.ROWS_NUMBER)] for _ in range(Board.COLUMNS_NUMBER)
        ]  # 10x10 empty board

        boats = [4, 3, 2, 1]
        empty_cells = Board.ROWS_NUMBER * Board.COLUMNS_NUMBER
        board_instance = Board(row_hints, column_hints, board, boats, empty_cells)

        L_T_pos = []

        for _ in range(hints_number):
            hint = sys.stdin.readline().strip().split("\t")[1:]
            row = int(hint[0])
            column = int(hint[1])
            letter = hint[2]

            if letter == "C":
                board_instance.boats[0] -= 1

            if letter in ("L", "T"):
                L_T_pos.append((row, column, letter))

            board_instance.place_symbol(letter, row, column)

        for symbol in L_T_pos:
            row = symbol[0]
            col = symbol[1]
            i = 1
            if symbol[2] == "L":
                while board_instance.get_value(row, col + i) == "M":
                    i += 1

                if board_instance.get_value(row, col + i) == "R":
                    board_instance.boats[i] -= 1

            elif symbol[2] == "T":
                while board_instance.get_value(row + i, col) == "M":
                    i += 1

                if board_instance.get_value(row + i, col) == "B":
                    board_instance.boats[i] -= 1

        return board_instance


class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""

        super().__init__(BimaruState(board))

    def actions(self, state: BimaruState) -> List[Tuple[int, int, int, int]]:
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""

        return state.board.calculate_placeable_boats()

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""

        row, col, size, direction, _ = action

        return BimaruState(state.board.place_boat(row, col, size, direction))

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""

        return state.board.is_goal()

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        pass


if __name__ == "__main__":
    board_instance = Board.parse_instance()
    board_instance.cleanup()
    node = depth_first_tree_search(Bimaru(board_instance))

    if node:
        print(node.state.board, end="")
