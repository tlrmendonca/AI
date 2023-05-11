# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

import sys
from sys import (
    stdin
)
from enum import Enum

from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)

class TileState(Enum):
    CENTER = 1
    UP = 2
    DOWN = 3
    LEFT = 4
    RIGHT = 5
    MID = 6
    MID_HORIZONTAL = 7
    MID_VERTICAL = 8
    WATER = 9
    EMPTY = 10

class Action:
    def __init__(self, initial, final):
        self.initial = initial
        self.final = final

    def getInitial(self):
        return self.initial
    
    def getFinal(self):
        return self.final

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

    row_values = list()
    column_values = list()
    modified_row_values = list()
    modified_column_values = list()
    board_matrix = list()

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        # TODO
        pass

    def adjacent_vertical_values(self, row: int, col: int):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        # TODO
        pass

    def adjacent_horizontal_values(self, row: int, col: int):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        # TODO
        pass

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 bimaru.py < input_T01

            > from sys import stdin
            > line = stdin.readline().split()
        """

        row = stdin.readline().split()
        column = stdin.readline().split()
        n = stdin.readline()
        board = Board()
        for i in range(1,11):
            board.row_values.append(row[i])
            board.modified_row_values.append(row[i])

        for i in range(1,11):
            board.column_values.append(column[i])
            board.modified_column_values.append(column[i])

        for i in range(0,10):
            row = list()
            for j in range(0,10):
                row.append(TileState.EMPTY)
            board.board_matrix.append(row)
            
        
        for i in range(0,n):
            hint = stdin.readline()
            x = hint[1]
            y = hint[2]
            tile_type = hint[3]
            #W (water), C (circle), T (top), M (middle),B (bottom), L (left) e R (right).
            if tile_type == 'W':
                real_type = TileState.WATER
            elif tile_type == 'C':
                real_type = TileState.CENTER
            elif tile_type == 'T':
                real_type = TileState.UP
            elif tile_type == 'M':
                real_type = TileState.MIDDLE
            elif tile_type == 'B':
                real_type = TileState.DOWN
            elif tile_type == 'L':
                real_type = TileState.LEFT
            elif tile_type == 'R':
                real_type = TileState.RIGHT
            board.board_matrix[x][y] = real_type
        return board
    


class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.initial = board

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
    board = Board.parse_instance
    bimaru = Bimaru(board)
