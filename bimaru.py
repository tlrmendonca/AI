# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

import numpy as np
from sys import (
    stdin
)
from enum import Enum
import copy as copy
from pickle import loads, dumps
from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_graph_search,
    greedy_search,
    recursive_best_first_search,
)

CENTER = 'C'
UP = 'T'
DOWN = 'B'
LEFT = 'L'
RIGHT = 'R'
MID = 'M'
MID_HORIZONTAL = 'MH'
MID_VERTICAL = 'MV'
WATER = '~'
EMPTY = '.'

FILL_ROW = 1
FILL_COLUMN = 2
FILL_TYLE = 3

class Line:
    def __init__(self,total,water,boats):
        self.total = total
        self.water = water
        self.boats = boats

    def checkWater(self):
        if(self.total - self.boats == 0):
            return True

    def checkFill(self):
        return 10 - self.water - self.boats == self.total
        
    def addWater(self):
        self.water += 1

    def addBoat(self):
        self.boats += 1

    def fullWater(self):
        return 10 - self.total <= self.water
    
    def fullBoat(self):
        return self.total - self.boats <= 0

    def getBoatProbability(self) -> int:
        return (self.total - self.boats) // (10 - self.boats - self.water)
    
    def getWaterProbability(self) -> int:
        return 100 - self.getBoatProbability()

class Action:
    def __init__(self, type, value, x):
        self.type = type
        self.value = value
        self.x = x
        self.y = '-'
    
    def __init__(self, type, value, x, y):
        self.type = type
        self.value = value
        self.x = x
        self.y = y
    
    def toString(self):
        return str(self.type) + " " + str(self.value) + " " + str(self.x) + " " + str(self.y)

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

    board_matrix = list() #board representation
    rows = list() #list of Line values
    columns = list() #list of Column values

    placed_boats : int = 0
    placed_waters : int = 0

    def update(self):
        pass

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        return self.board_matrix[row][col]
    
    def set_value(self, row: int, col: int, type):
        self.board_matrix[row][col] = type
        
        if(type == WATER):
            self.rows[row].addWater()
            self.columns[col].addWater()
            self.placed_waters += 1
        else:
            self.rows[row].addBoat()
            self.columns[col].addBoat()
            self.placed_boats += 1

    def is_boat_position(self,row,col):
        return self.board_matrix[row][col] != 'None' and self.board_matrix[row][col] != WATER and self.board_matrix[row][col] != EMPTY
    
    def is_boat(self,tile):
        return tile != 'None' and tile != WATER and tile != EMPTY

    def is_water(self,tile):
        return tile == WATER

    def adjacent_vertical_values(self, row: int, col: int):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        values = ['None', 'None']
        if(row > 0):
            values[0] = self.board_matrix[row-1][col]
        if(row < 9):
            values[1] = self.board_matrix[row+1][col]
        return values

    def adjacent_horizontal_values(self, row: int, col: int):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        values = ['None', 'None']
        if(col > 0):
            values[0] = self.board_matrix[row][col-1]
        if(col < 9):
            values[1] = self.board_matrix[row][col+1]
        return values
    
    def diagonal_values(self,row,col):
        values = ['None', 'None', 'None', 'None']
        if(col > 0 and row > 0):
            values[0] = self.board_matrix[row-1][col-1]
        if(col > 0 and row < 9):
            values[1] = self.board_matrix[row+1][col-1]
        if(row > 0 and col < 9):
            values[2] = self.board_matrix[row-1][col+1]
        if(row < 9 and col < 9):
            values[3] = self.board_matrix[row+1][col+1]
        return values
    
    def put_water_diagonal_values(self,row,col):
        i = 0
        if(col > 0 and row > 0 and self.board_matrix[row-1][col-1] == EMPTY):
            i += 1
            self.set_value(row-1,col-1,WATER)
        if(col > 0 and row < 9 and self.board_matrix[row+1][col-1] == EMPTY):
            i += 1
            self.set_value(row+1,col-1,WATER)
        if(row > 0 and col < 9 and self.board_matrix[row-1][col+1] == EMPTY):
            i += 1
            self.set_value(row-1,col+1,WATER)
        if(row < 9 and col < 9 and self.board_matrix[row+1][col+1] == EMPTY):
            i += 1
            self.set_value(row+1,col+1,WATER)
        return i 
    
    def put_water_vertical(self,row,col):
        if(row > 0):
            self.board_matrix[row-1][col] = WATER
        if(row < 9):
            self.board_matrix[row+1][col] = WATER
    
    def put_water_horizontal(self,row,col):
        if(col > 0):
            self.board_matrix[row][col-1] = WATER
        if(col < 9):
            self.board_matrix[row][col+1] = WATER
    
    def isBlockedBoat(self,row,col):
        for tile in self.adjacent_vertical_values(row,col):
            if(tile != WATER and tile != EMPTY and tile != 'None'):
                return True
        for tile in self.adjacent_horizontal_values(row,col):
            if(tile != WATER and tile != EMPTY and tile != 'None'):
                return True
        for tile in self.diagonal_values(row,col):
            if(tile != WATER and tile != EMPTY and tile != 'None'):
                return True
        return False
    
    def print(self):
        print('   ', end='')
        for i in range(0,10):
            print(' ' + str(self.columns[i].total) + ' ', end='')
        print('')
        for i in range(0,10):
            print(str(self.rows[i].total) + ' [',end='')
            for j in range(0,10):
                print(' ' + self.board_matrix[i][j] + ' ', end='')
            print(']')
    
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
        n = stdin.readline().split()
        board = Board()

        for i in range(1,11):
            line = Line(int(row[i]),0,0)
            board.rows.append(line)

        for i in range(1,11):
            line = Line(int(column[i]),0,0)
            board.columns.append(line)

        for i in range(0,10):
            row = [EMPTY] * 10
            board.board_matrix.append(row)
            
        for i in range(0,int(n[0])):
            hint = stdin.readline().split()
            x = int(hint[1])
            y = int(hint[2])
            tile_type = hint[3]
            #W (water), C (circle), T (top), M (middle),B (bottom), L (left) e R (right).
            if tile_type == 'W':
                real_type = WATER
            else:
                board.put_water_diagonal_values(x,y)
                if tile_type == 'C':
                    board.put_water_horizontal(x,y)
                    board.put_water_vertical(x,y)
                    real_type = CENTER
                elif tile_type == 'T':
                    board.put_water_horizontal(x,y)
                    real_type = UP
                elif tile_type == 'M':
                    real_type = MID
                elif tile_type == 'B':
                    board.put_water_horizontal(x,y)
                    real_type = DOWN
                elif tile_type == 'L':
                    board.put_water_vertical(x,y)
                    real_type = LEFT
                elif tile_type == 'R':
                    board.put_water_vertical(x,y)
                    real_type = RIGHT
            
            board.set_value(x, y, real_type)
        print("Board created!")
        print("Placed stuff: " + str(board.placed_waters + board.placed_boats))
        return board
    


class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.initial = BimaruState(board)

    def countEmpty(self,board):
        total=0
        for i in range(0,10):
            for j in range(0,10):
                if(board.board_matrix[i][j] == EMPTY):
                    total+=1
        return total
    
    def update_boats(self,state: BimaruState):
        board: Board = state.board

        for i in range(0,10):
            for j in range(0,10):
                vertical_values = board.adjacent_vertical_values(i,j)
                up = vertical_values[0]
                down = vertical_values[1]
                horizontal_values = board.adjacent_horizontal_values(i,j)
                left = horizontal_values[0]
                right = horizontal_values[1]

                if(board.is_boat_position(i,j) and not board.is_boat(up) and not board.is_boat(down) and not board.is_boat(left) and not board.is_boat(right)):
                    board.set_value(i,j,CENTER)
                    board.put_water_horizontal(i,j)
                    board.put_water_vertical(i,j)

                
#CENTER = 'C'
#UP = 'T'
#DOWN = 'B'
#LEFT = 'L'
#RIGHT = 'R'
#MID = 'M'
#MID_HORIZONTAL = 'MH'
#MID_VERTICAL = 'MV'
#WATER = '~'
#EMPTY = '.'
    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        actionList = list()
        for i in range(0,10):
            for j in range(0,10):
                if ((state.board.board_matrix[i][j] == EMPTY) and not (state.board.rows[i].fullBoat()) and not (state.board.columns[j].fullBoat()) and not (state.board.isBlockedBoat(i,j))):
                    action = Action(FILL_TYLE,MID,i,j)
                    actionList.append(action)
                if((state.board.board_matrix[i][j] == EMPTY) and not (state.board.rows[i].fullWater()) and not (state.board.columns[j].fullWater())):
                    action = Action(FILL_TYLE,WATER,i,j)
                    actionList.append(action)
        return list(actionList)
    
    def result(self, state_original: BimaruState, action: Action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        #print("Using Action: " + str(action.type) + str(action.value))
        state = copy.copy(state_original)
        state.board = copy.copy(state_original.board)
        state.board.board_matrix = copy.deepcopy(state_original.board.board_matrix)
        state.board.rows = copy.deepcopy(state_original.board.rows)
        state.board.columns = copy.deepcopy(state_original.board.columns)
        state.board.placed_boats : copy.deepcopy(state_original.board.placed_boats)
        state.board.placed_waters : copy.deepcopy(state_original.board.placed_waters)

        if(action.type == FILL_ROW):
            if(action.value != WATER):
                for i in range(0,10):
                    state.board.set_value(action.x,i,action.value)
                    state.board.put_water_diagonal_value(action.x,i)
            else:
                for i in range(0,10):
                    state.board.set_value(action.x,i,action.value)
        elif(action.type == FILL_COLUMN):
            if(action.value != WATER):
                for i in range(0,10):
                    state.board.set_value(i,action.x,action.value)
                    state.board.put_water_diagonal_value(i,action.x)
            else:
                for i in range(0,10):
                    state.board.set_value(i,action.x,action.value)
        elif(action.type == FILL_TYLE):
            #if(action.value == MID):
                #print("Placing it on: " + str(state.board.board_matrix[action.x][action.y]))
            state.board.set_value(action.x,action.y,action.value)
            #if(action.value != WATER):
            #    print("diagonal")
            #   state.board.put_water_diagonal_values(action.x,action.y)

        #print("Placed stuff: " + str(state.board.placed_waters + state.board.placed_boats))
        #print("Spots left: " + str(self.countEmpty(state.board)))
        #print(state.id)
        self.update_boats(state)
        return state
            

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        #print("Goal Test: "+ str(state.board.placed_waters + state.board.placed_boats))
        if(self.countEmpty(state.board)):
            return False
        return True

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        return 20 - node.state.board.placed_boats


if __name__ == "__main__":
    print("Program Started")
    board = Board.parse_instance()
    bimaru = Bimaru(board)

    board.print()
    # i = 0;
    # for action in bimaru.actions(bimaru.initial):
    #     print(str(i) + ':' + action.toString())
    #     i = i + 1
    goal_node = depth_first_graph_search(bimaru)

    print("Is goal?", bimaru.goal_test(goal_node.state))
    print("Solution:\n", goal_node.state.board.print(), sep="")