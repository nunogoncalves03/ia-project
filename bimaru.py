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

        return self.board[row][col]

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


    def place_water_around(self, row: int, col: int):
        """Places water around the given cell
        accordingly to the symbol it holds. """

        symbol = self.board[row][col]
        
        if symbol in ('C', 'c'):
            self.place_water_around_C(row, col)
        elif symbol in ('M', 'm'):
            pass
        elif symbol in ('T', 't', 'B', 'b'):
            self.place_water_around_T_B(symbol, row, col)        
        elif symbol in ('L', 'l','R', 'r'):
            self.place_water_around_R_L(symbol, row, col)

    def place_water_around_T_B(self, symbol: str, row: int, col: int):
        # upper row
        if row > 0:
            if col > 0:
                self.board[row - 1][col - 1] = 'w'
            # only cover the cell above the symbol if it's T
            if symbol in ('T', 't'):
                self.board[row - 1][col] = 'w'
            if col < Board.COLUMNS_NUMBER - 1:
                self.board[row - 1][col + 1] = 'w'
            
            # only cover the further side cells above the symbol if it's B
            if symbol in ('B', 'b') and row > 1:
                if col > 0:
                    self.board[row - 2][col - 1] = 'w'
                if col < Board.COLUMNS_NUMBER - 1:
                    self.board[row - 2][col + 1] = 'w'
        # to the left
        if col > 0:
            self.board[row][col - 1] = 'w'
        # to the right
        if col < Board.COLUMNS_NUMBER - 1:
            self.board[row][col + 1] = 'w'
        # inferior row
        if row < Board.COLUMNS_NUMBER - 1:
            if col > 0:
                self.board[row + 1][col - 1] = 'w'
            # only cover the cell underneath the symbol if it's B
            if symbol in ('B', 'b'):
                self.board[row + 1][col] = 'w'
            if col < Board.COLUMNS_NUMBER - 1:
                self.board[row + 1][col + 1] = 'w'

            # only cover the further side cells underneath the symbol if it's T
            if symbol in ('T', 't') and row < Board.COLUMNS_NUMBER - 2:
                    if col > 0:
                        self.board[row + 2][col - 1] = 'w'
                    if col < Board.COLUMNS_NUMBER - 1:
                        self.board[row + 2][col + 1] = 'w'

    def place_water_around_R_L(self, symbol: str, row: int, col: int):
        # upper row
        if row > 0:
            # only cover the further left side cell above the symbol if it's R
            if symbol in ('R', 'r') and col > 1:
                self.board[row - 1][col - 2] = 'w'

            if col > 0:
                self.board[row - 1][col - 1] = 'w'
            self.board[row - 1][col] = 'w'
            if col < Board.COLUMNS_NUMBER - 1:
                self.board[row - 1][col + 1] = 'w'

            # only cover the further right side cell above the symbol if it's L
            if symbol in ('L', 'l') and col < Board.COLUMNS_NUMBER - 2:
                self.board[row - 1][col + 2] = 'w'
        # to the right
        if symbol in ('R', 'r') and col < Board.COLUMNS_NUMBER - 1:
            self.board[row][col + 1] = 'w'
        # to the left
        if symbol in ('L', 'l') and col > 0:
            self.board[row][col - 1] = 'w'
        # inferior row
        if row < Board.COLUMNS_NUMBER - 1:
            # only cover the further left side cell underneath the symbol if it's R
            if symbol in ('R', 'r') and col > 1:
                self.board[row + 1][col - 2] = 'w'

            if col > 0:
                self.board[row + 1][col - 1] = 'w'
            self.board[row + 1][col] = 'w'
            if col < Board.COLUMNS_NUMBER - 1:
                self.board[row + 1][col + 1] = 'w'

            # only cover the further right side cell underneath the symbol if it's L
            if symbol in ('L', 'l') and col < Board.COLUMNS_NUMBER - 2:
                self.board[row + 1][col + 2] = 'w'

    def place_water_around_C(self, row: int, col: int):
        # upper row
        if row > 0:
            if col > 0:
                self.board[row - 1][col - 1] = 'w'
            self.board[row - 1][col] = 'w'
            if col < Board.COLUMNS_NUMBER - 1:
                self.board[row - 1][col + 1] = 'w'
        # to the left
        if col > 0:
            self.board[row][col - 1] = 'w'
        # to the right
        if col < Board.COLUMNS_NUMBER - 1:
            self.board[row][col + 1] = 'w'
        # inferior row
        if row < Board.COLUMNS_NUMBER - 1:
            if col > 0:
                self.board[row + 1][col - 1] = 'w'
            self.board[row + 1][col] = 'w'
            if col < Board.COLUMNS_NUMBER - 1:
                self.board[row + 1][col + 1] = 'w'

    def place_water_around_M(self, symbol: str, row: int, col: int):
        pass

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
            board_instance.place_water_around(i, j)

    for _ in range(20):
        for i in range(Board.ROWS_NUMBER):
            board_instance.place_water_row(i)
            board_instance.place_water_column(i)
            board_instance.place_boats_row(i)
            board_instance.place_boats_column(i)

    print(board_instance, end="\n---------------\n")
