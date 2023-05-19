# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 56:
# 102802 Fabio Mata
# 103392 Nuno Goncalves

import sys
from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)
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

    # TODO: outros metodos da classe


class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    ROWS_NUMBER = 10
    COLUMNS_NUMBER = 10
    OUT_OF_BOUNDS = 'x'

    def __init__(self, row_hints: List[int], column_hints: List[int], board: List[List[str]]):
        self.board = board
        self.row_hints = row_hints
        self.column_hints = column_hints

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        if row >= 0 and row <= Board.ROWS_NUMBER - 1:
            if col >= 0 and col <= Board.COLUMNS_NUMBER - 1:
                return self.board[row][col]
        
        return Board.OUT_OF_BOUNDS
    
    def place_symbol(self, symbol: str, row: int, col: int):
        """Places the given symbol in the given position if valid,
        does nothing otherwise. """
        if row >= 0 and row <= Board.ROWS_NUMBER - 1:
            if col >= 0 and col <= Board.COLUMNS_NUMBER - 1:
                self.board[row][col] = symbol

    def adjacent_vertical_values(self, row: int, col: int) -> Tuple[str, str]:
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        
        return (self.board[row - 1][col] if row > 0 else Board.OUT_OF_BOUNDS,
                self.board[row + 1][col] if row < Board.ROWS_NUMBER - 1 else Board.OUT_OF_BOUNDS)

    def adjacent_horizontal_values(self, row: int, col: int) -> Tuple[str, str]:
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""

        return (self.board[row][col - 1] if col > 0 else Board.OUT_OF_BOUNDS,
                self.board[row][col + 1] if col < Board.COLUMNS_NUMBER - 1 else Board.OUT_OF_BOUNDS)
    
    def adjacent_diagonal_values(self, row: int, col: int) -> Tuple[str, str, str, str]:
        """Devolve os valores em cima à esquerda,
        em cima à direita, em baixo à direita e em baixo à esquerda,
        respectivamente."""

        top_left = self.board[row - 1][col - 1] if row > 0 and col > 0 \
                                                else Board.OUT_OF_BOUNDS 

        top_right = self.board[row - 1][col + 1] if row > 0 and col < Board.COLUMNS_NUMBER - 1 \
                                                else Board.OUT_OF_BOUNDS 

        bottom_right = self.board[row + 1][col + 1] if row < Board.ROWS_NUMBER - 1 and col < Board.COLUMNS_NUMBER - 1 \
                                                    else Board.OUT_OF_BOUNDS 

        bottom_left = self.board[row + 1][col - 1] if row < Board.ROWS_NUMBER - 1 and col > 0 \
                                                    else Board.OUT_OF_BOUNDS 
        
        return (top_left, top_right, bottom_right, bottom_left)


    def process_cell(self, row: int, col: int):
        """Places water and $ around the given cell
        accordingly to the symbol it holds. """

        symbol = self.board[row][col]
        
        if symbol in ('C', 'c'):
            self.process_C(row, col)
        elif symbol in ('M', 'm'):
            self.process_M(row, col)
        elif symbol in ('T', 't', 'B', 'b'):
            self.process_T_B(symbol, row, col)        
        elif symbol in ('L', 'l','R', 'r'):
            self.process_L_R(symbol, row, col)

    def process_T_B(self, symbol: str, row: int, col: int):
        # upper row
        self.place_symbol('w', row - 1, col - 1)
        # only cover the cell above the symbol if it's T
        if symbol in ('T', 't'):
            self.place_symbol('w', row - 1, col)
        else:
            self.place_symbol('$', row - 1, col)
        self.place_symbol('w', row - 1, col + 1)
        
        # only cover the further side cells above the symbol if it's B
        if symbol in ('B', 'b'):
            self.place_symbol('w', row - 2, col - 1)
            self.place_symbol('w', row - 2, col + 1)

        # to the left
        self.place_symbol('w', row, col - 1)

        # to the right
        self.place_symbol('w', row, col + 1)

        # inferior row
        self.place_symbol('w', row + 1, col - 1)
        # only cover the cell underneath the symbol if it's B
        if symbol in ('B', 'b'):
            self.place_symbol('w', row + 1, col)
        else:
            self.place_symbol('$', row + 1, col)
        self.place_symbol('w', row + 1, col + 1)
        
        # only cover the further side cells underneath the symbol if it's T
        if symbol in ('T', 't'):
            self.place_symbol('w', row + 2, col - 1)
            self.place_symbol('w', row + 2, col + 1)


    def process_L_R(self, symbol: str, row: int, col: int):
        # upper row
        # only cover the further left side cell above the symbol if it's R
        if symbol in ('R', 'r'):
            self.place_symbol('w', row - 1, col - 2)
        self.place_symbol('w', row - 1, col - 1)
        self.place_symbol('w', row - 1, col)
        self.place_symbol('w', row - 1, col + 1)
        # only cover the further right side cell above the symbol if it's L
        if symbol in ('L', 'l'):
            self.place_symbol('w', row - 1, col + 2)

        # to the right
        if symbol in ('R', 'r'):
            self.place_symbol('w', row, col + 1)
        else:
            self.place_symbol('$', row, col + 1)
            
        # to the left
        if symbol in ('L', 'l'):
            self.place_symbol('w', row, col - 1)
        else:
            self.place_symbol('$', row, col - 1)

        # inferior row
        # only cover the further left side cell underneath the symbol if it's R
        if symbol in ('R', 'r'):
            self.place_symbol('w', row + 1, col - 2)
        self.place_symbol('w', row + 1, col - 1)
        self.place_symbol('w', row + 1, col)
        self.place_symbol('w', row + 1, col + 1)
        # only cover the further right side cell underneath the symbol if it's L
        if symbol in ('L', 'l'):
            self.place_symbol('w', row + 1, col + 2)

    def process_C(self, row: int, col: int):
        # upper row
        self.place_symbol('w', row - 1, col - 1)
        self.place_symbol('w', row - 1, col)
        self.place_symbol('w', row - 1, col + 1)
        # to the left
        self.place_symbol('w', row, col - 1)
        # to the right
        self.place_symbol('w', row, col + 1)
        # inferior row
        self.place_symbol('w', row + 1, col - 1)
        self.place_symbol('w', row + 1, col)
        self.place_symbol('w', row + 1, col + 1)

    def process_M(self, row: int, col: int):
        vertical_adj_values = self.adjacent_vertical_values(row, col)
        horizontal_adj_values = self.adjacent_horizontal_values(row, col)

        # check if M is part of a horizontally displayed ship
        if 'W' in vertical_adj_values or 'w' in vertical_adj_values or \
            row == Board.ROWS_NUMBER - 1 or row == 0 or \
            any(map(lambda x: x not in ('', 'W', 'w', Board.OUT_OF_BOUNDS),
                    horizontal_adj_values)):
            if horizontal_adj_values[0] == '':
                self.place_symbol('$', row, col - 1)
            if horizontal_adj_values[1] == '':
                self.place_symbol('$', row, col + 1)
            for i in (row - 1, row + 1):
                for j in (col - 2, col - 1, col, col + 1, col + 2):
                    self.place_symbol('w', i, j)
        # check if M is part of a vertically displayed ship
        elif 'W' in horizontal_adj_values or 'w' in horizontal_adj_values or \
            col == Board.COLUMNS_NUMBER - 1 or col == 0 or \
            any(map(lambda x: x not in ('', 'W', 'w', Board.OUT_OF_BOUNDS),
                    vertical_adj_values)):
            if vertical_adj_values[0] == '':
                self.place_symbol('$', row - 1, col)
            if vertical_adj_values[1] == '':
                self.place_symbol('$', row + 1, col)
            for i in (row - 2, row - 1, row, row + 1, row + 2):
                for j in (col - 1, col + 1):
                    self.place_symbol('w', i, j)


    def place_water_row(self, row: int):
        symbol_counter = 0
        for col in range(Board.COLUMNS_NUMBER):
            if self.board[row][col] not in ('', 'w', 'W'):
                symbol_counter += 1
        
        if symbol_counter == self.row_hints[row]:
            for col in range(Board.COLUMNS_NUMBER):
                if self.board[row][col] == '':
                    self.board[row][col] = 'w'

    def place_water_column(self, col: int):
        symbol_counter = 0
        for row in range(Board.ROWS_NUMBER):
            if self.board[row][col] not in ('', 'w', 'W'):
                symbol_counter += 1
        
        if symbol_counter == self.column_hints[col]:
            for row in range(Board.ROWS_NUMBER):
                if self.board[row][col] == '':
                    self.board[row][col] = 'w'

    def place_boats_row(self, row: int):
        boat_counter = 0
        empty_counter = 0
        for col in range(Board.COLUMNS_NUMBER):
            if self.board[row][col] not in ('', 'w', 'W'):
                boat_counter += 1
            elif self.board[row][col] == '':
                empty_counter += 1
        
        if boat_counter + empty_counter == self.row_hints[row]:
            for col in range(Board.COLUMNS_NUMBER):
                if self.board[row][col] == '':
                    self.board[row][col] = '$'

    def place_boats_column(self, col: int):
        boat_counter = 0
        empty_counter = 0
        for row in range(Board.ROWS_NUMBER):
            if self.board[row][col] not in ('', 'w', 'W'):
                boat_counter += 1
            elif self.board[row][col] == '':
                empty_counter += 1
        
        if boat_counter + empty_counter == self.column_hints[col]:
            for row in range(Board.ROWS_NUMBER):
                if self.board[row][col] == '':
                    self.board[row][col] = '$'

    def replace_placeholders(self):
        for row in range(Board.ROWS_NUMBER):
            for col in range(Board.COLUMNS_NUMBER):
                if self.get_value(row, col) == "$":

                    if self.adjacent_horizontal_values(row, col)[0] == "L" \
                        or (self.adjacent_horizontal_values(row, col)[1] not in (
                        "",
                        "w",
                        "W",
                        Board.OUT_OF_BOUNDS) and self.adjacent_horizontal_values(row, col)[0] not in ("", "$")):
                        if self.adjacent_horizontal_values(row, col)[0] != "L":
                            self.place_symbol("l", row, col)

                        i = 1
                        while self.get_value(row, col + i) in ("$", "m", "M"):
                            if self.get_value(row, col + i) == "M":
                                i += 1
                                continue

                            self.place_symbol("m", row, col + i)
                            i += 1

                        if self.get_value(row, col + i) == "R":
                            continue

                        if self.get_value(row, col + i) != "":
                            self.place_symbol("r", row, col + i - 1)

                    elif self.adjacent_vertical_values(row, col)[0] == "T" \
                        or (self.adjacent_vertical_values(row, col)[1] not in (
                        "",
                        "w",
                        "W",
                        Board.OUT_OF_BOUNDS) and self.adjacent_vertical_values(row, col)[0] not in ("", "$")):
                        if self.adjacent_vertical_values(row, col)[0] != "T":
                            self.place_symbol("t", row, col)

                        i = 1
                        while self.get_value(row + i, col) in ("$", "m", "M"):
                            if self.get_value(row + i, col) == "M":
                                i += 1
                                continue

                            self.place_symbol("m", row + i, col)
                            i += 1

                        if self.get_value(row + i, col) == "B":
                            continue

                        if self.get_value(row + i, col) != "":
                            self.place_symbol("b", row + i - 1, col)

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

    def __str__(self):
        """Returns a string representation of the Board as described in
        topic 4.2 of the statement. """

        string = ""

        for row in self.board:
            for symbol in row:
                if symbol == '':
                    symbol = ' '
                elif symbol == 'w':
                    symbol = '.'
                string += symbol
            string += '\n'
        
        return string

    @staticmethod
    def parse_instance() -> Board:
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board."""


        row_hints = sys.stdin.readline().split('\t')[1:]  # ignore ROW keyword
        row_hints = [int(x) for x in row_hints]

        column_hints = sys.stdin.readline().split('\t')[1:]  # ignore COLUMN keyword
        column_hints = [int(x) for x in column_hints]

        hints_number = int(sys.stdin.readline())
        
        board = [["" for _ in range(Board.ROWS_NUMBER)] for _ in range(Board.COLUMNS_NUMBER)]  # 10x10 empty board

        for i in range(hints_number):
            hint = sys.stdin.readline().strip().split('\t')[1:]
            row = int(hint[0])
            column = int(hint[1])
            letter = hint[2]

            board[row][column] = letter


        return Board(row_hints, column_hints, board)
    
    # TODO: outros metodos da classe


class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        # TODO
        pass

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        # TODO
        pass

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        # TODO
        pass

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        # TODO
        pass

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    # TODO: outros metodos da classe


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    board_instance = Board.parse_instance()

    print(f"Row hints: {board_instance.row_hints}")
    print(f"Column hints: {board_instance.column_hints}")

    for i in range(Board.ROWS_NUMBER):
        for j in range(Board.COLUMNS_NUMBER):
            board_instance.process_cell(i, j)

    for i in range(Board.ROWS_NUMBER):
        for j in range(Board.COLUMNS_NUMBER):
            board_instance.process_cell(i, j)

    for _ in range(20):
        for i in range(Board.ROWS_NUMBER):
            board_instance.place_water_row(i)
            board_instance.place_water_column(i)
            board_instance.place_boats_row(i)
            board_instance.place_boats_column(i)

    print(board_instance, end="\n---------------\n")

    board_instance.replace_placeholders()

    print(board_instance, end="\n---------------\n")
