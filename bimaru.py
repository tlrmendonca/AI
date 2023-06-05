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
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)

CENTER = 'C'
UP = 'T'
DOWN = 'B'
LEFT = 'L'
RIGHT = 'R'
MID = 'M'
MID_HORIZONTAL = 'H'
MID_VERTICAL = 'V'
WATER = '.'
EMPTY = ' '

FILL_ROW = 1
FILL_COLUMN = 2
FILL_TILE = 3

VERTICAL = 1
HORIZONTAL = 2

class Line:
    def __init__(self,total,water,boats):
        self.total = total
        self.water = water
        self.boats = boats
        self.isFull = False

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
        return self.water >= 10 - self.total
    
    def fullBoat(self):
        return self.total - self.boats <= 0

    def getBoatProbability(self) -> int:
        return (self.total - self.boats) // (10 - self.boats - self.water)
    
    def getWaterProbability(self) -> int:
        return 100 - self.getBoatProbability()

class Action:
    '''Class that represents an action to be taken on the board
    Consists of a boat size and tuple of tuples with coordinates'''
    def __init__(self, boat_size, coordinates, orientation):
        self.boat_size = boat_size
        self.coordinates = coordinates
        self.orientation = VERTICAL
        
    
    def toString(self):
        return str(self.boat_size) + " " + str(self.coordinates)

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
    hints = list()

    placed_boats : int = 0
    placed_waters : int = 0

    def update(self):
        pass

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        return self.board_matrix[row][col]
    
    def set_value(self, row: int, col: int, type):
        if(type == WATER and self.board_matrix[row][col] == EMPTY):
            self.rows[row].addWater()
            self.columns[col].addWater()
            self.placed_waters += 1
        elif(self.is_boat(type) and self.board_matrix[row][col] == EMPTY):
            self.put_water_diagonal_values(row,col)
            self.rows[row].addBoat()
            self.columns[col].addBoat()
            self.placed_boats += 1
        self.board_matrix[row][col] = type

    def boat_available(self,row,col,type='Mid'):
      '''Defines if position [row,col] is available for a boat
      Note: THIS FUNCTION SHOULD NOT BE USED OUTSIDE THE PROPER CONTEXT
      Only available to check boat positioning where 'Begin' and 'End'
      are set as the top and bottom or left and right peices of the boat'''

      # position needs to empty or any type of boat and lines not full
      # we will check in later stages if the boat is adequate or not, when we
      # check for adjacent values
      if(self.board_matrix[row][col] == WATER):
        return False
      # exceptions: begin and end can't be middle (impossible to check on this later)
      if(type == 'Begin' and self.board_matrix[row][col] == MID or type == 'End' and self.board_matrix[row][col] == MID):
        return False
      if(self.rows[row].fullBoat() or self.columns[col].fullBoat()):
        return False

      vertical = self.adjacent_vertical_values(row,col)
      horizontal = self.adjacent_horizontal_values(row,col)
      diagonal = self.diagonal_values(row,col)

      # vertically top has to be empty, water, none, a top end or a middle
      # bottom has to be empty, water, none, a bottom end or a middle
      if(vertical[0] != WATER and vertical[0] != EMPTY and vertical[0] != 'None' and vertical[0] != UP and vertical[0] != MID
         and vertical[1] != WATER and vertical[1] != EMPTY and vertical[1] != 'None' and vertical[1] != DOWN and vertical[0] != MID):
        return False
      # exceptions: beggining below up or end above bottom
      if ((vertical[0] == UP and type == 'Begin') or (vertical[1] == DOWN and type == 'End')):
        return False
      
      # horizontally left has to be empty, water, none, a left end or a middle
      # right has to be empty, water, none, a right end or a middle
      if(horizontal[0] != WATER and horizontal[0] != EMPTY and horizontal[0] != 'None' and horizontal[0] != LEFT and vertical[0] != MID
          and horizontal[1] != WATER and horizontal[1] != EMPTY and horizontal[1] != 'None' and horizontal[1] != RIGHT and vertical[0] != MID):
        return False
      # exceptions: beggining right of left or end left of right
      if ((horizontal[0] == LEFT and type == 'Begin') or (horizontal[1] == RIGHT and type == 'End')):
        return False

      # diagonally all spaces have to be empty, water or none
      for tile in diagonal:
        if(tile != WATER and tile != EMPTY and tile != 'None'):
          return False

      # a lof of checks but also simplifies boat positioning
      return True

    def enough_space(self,orientation,row,col,size):
      '''Note: I wish I didn't have to write this
      This is needed to calculate available space since we can use already placed boats,
      so we have to go to each space and check if it's empty or not'''
      num_reused = 0

      if(orientation == 'Row'):
        for i in range(0,size):
          if(self.is_boat(self.board_matrix[row][col+i])):
            num_reused += 1
        return (self.rows[row].total - self.rows[row].boats + num_reused) >= size
      
      if(orientation == 'Column'):
        for i in range(0,size):
          if(self.is_boat(self.board_matrix[row+i][col])):
            num_reused += 1
        return (self.columns[col].total - self.columns[col].boats + num_reused) >= size
      # "total" is the total number of boats to complete the line, "boats" is the already placed boats
      # (including hints), "num_reused" is the placed boats in the required spaces

    def is_boat_position(self,row,col):
        return self.board_matrix[row][col] != 'None' and self.board_matrix[row][col] != WATER and self.board_matrix[row][col] != EMPTY
    
    def is_boat(self,tile):
        return tile != 'None' and tile != WATER and tile != EMPTY

    def is_water(self,tile):
        return tile == WATER
    
    def is_mid(self,tile):
        return tile == MID or tile == MID_HORIZONTAL or tile == MID_VERTICAL
    
    def is_mid_position(self,row,col):
        tile = self.board_matrix[row][col]
        return tile == MID or tile == MID_HORIZONTAL or tile == MID_VERTICAL
    
    def is_corner(self,tile):
        return self.is_boat(tile) and not self.is_mid(tile)

    def adjacent_vertical_values(self, row: int, col: int):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        values = ['None', 'None']
        if(row > 0):
            values[0] = self.board_matrix[row-1][col] # up
        if(row < 9):
            values[1] = self.board_matrix[row+1][col] # down
        return values

    def adjacent_horizontal_values(self, row: int, col: int):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        values = ['None', 'None']
        if(col > 0):
            values[0] = self.board_matrix[row][col-1] # left
        if(col < 9):
            values[1] = self.board_matrix[row][col+1] # right
        return values
    
    def diagonal_values(self,row,col):
        values = ['None', 'None', 'None', 'None']
        if(col > 0 and row > 0):
            values[0] = self.board_matrix[row-1][col-1] # up-left
        if(row > 0 and col < 9):
            values[2] = self.board_matrix[row-1][col+1] # up-right
        if(col > 0 and row < 9):
            values[1] = self.board_matrix[row+1][col-1] # down-left
        if(row < 9 and col < 9):
            values[3] = self.board_matrix[row+1][col+1] # down-right
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
            self.set_value(row-1,col,WATER)
        if(row < 9):
            self.set_value(row+1,col,WATER)

    def put_boat_up(self,row,col):
        if(row > 0):
            self.set_value(row-1,col,MID_VERTICAL)

    def put_boat_down(self,row,col):
        if(row < 9):
            self.set_value(row+1,col,MID_VERTICAL)

    def put_water_up(self,row,col):
        if(row > 0):
            self.set_value(row-1,col,WATER)

    def put_water_down(self,row,col):
        if(row < 9):
            self.set_value(row+1,col,WATER)
    
    def put_water_horizontal(self,row,col):
        if(col > 0):
            self.set_value(row,col-1,WATER)
        if(col < 9):
            self.set_value(row,col+1,WATER)
    
    def put_water_left(self,row,col):
        if(col > 0):
            self.set_value(row,col-1,WATER)

    def put_water_right(self,row,col):
        if(col < 9):
            self.set_value(row,col+1,WATER)

    def put_boat_left(self,row,col):
        if(col > 0):
            self.set_value(row,col-1,MID_HORIZONTAL)
    
    def put_boat_right(self,row,col):
        if(col < 9):
            self.set_value(row,col+1,MID_HORIZONTAL)

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
        for i in range(0,10):
            for j in range(0,10):
                if((i,j) not in self.hints):
                    print(self.board_matrix[i][j].lower(), end='')
                else:
                    print(self.board_matrix[i][j], end='')
            print('')    

    def print2(self):
        print('   ', end='')
        for i in range(0,10):
            print(' ' + str(self.columns[i].total) + ' ', end='')
        print('')
        for i in range(0,10):
            print(str(self.rows[i].total) + ' [',end='')
            for j in range(0,10):
                if((i,j) not in self.hints):
                    print(' ' + self.board_matrix[i][j].lower() + ' ', end='')
                else:
                    print(' ' + self.board_matrix[i][j] + ' ', end='')
            print(']')
    def verify_lines(self):
        for i in range(0,10):
            if(self.rows[i].water + self.rows[i].total > 10):
                return False
            if(self.columns[i].water + self.columns[i].total > 10):
                return False
        return True
    
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

            # Save as hint
            board.hints.append((x,y))

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

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        actionList = list()

        #Try to find spots for 4-boat
        for i in range(0,7): #searching downwards orientation, starting at [i,j]
            for j in range(0,10):
                if (state.board.enough_space('Column', i, j, 4) and # There are enough spaces for a boat
                    state.board.boat_available(i,j,'Begin') and # All position are available
                    state.board.boat_available(i+1,j,'Middle') and
                    state.board.boat_available(i+2,j,'Middle') and
                    state.board.boat_available(i+3,j,'End')):
                    action = Action(4, ((i,j),(i+1,j),(i+2,j),(i+3,j)),VERTICAL)
                    if(self.result(state,action).board.verify_lines()):
                        actionList.append(action)
        for i in range(0,10): #searching rightwards orientation, starting at [i,j]
            for j in range(0,7):
                if (state.board.enough_space('Row', i, j, 4) and # There are enough spaces for a boat
                    state.board.boat_available(i,j,'Begin') and # All position are available
                    state.board.boat_available(i,j+1,'Middle') and
                    state.board.boat_available(i,j+2,'Middle') and
                    state.board.boat_available(i,j+3,'End')):
                    action = Action(4, ((i,j),(i,j+1),(i,j+2),(i,j+3)),HORIZONTAL)
                    if(self.result(state,action).board.verify_lines()):
                        actionList.append(action)

        #Try to find spots for 3-boat
        for i in range(0,8): #searching downwards orientation, starting at [i,j]
            for j in range(0,10):
                if (state.board.enough_space('Column', i, j, 3) and # There are enough spaces for a boat
                    state.board.boat_available(i,j,'Begin') and # All positions are available
                    state.board.boat_available(i+1,j,'Middle') and
                    state.board.boat_available(i+2,j,'End')):
                    action = Action(3, ((i,j),(i+1,j),(i+2,j)),VERTICAL )
                    if(self.result(state, action).board.verify_lines()):
                        actionList.append(action)
        for i in range(0,10): #searching rightwards orientation, starting at [i,j]
            for j in range(0,8):
                if (state.board.enough_space('Row', i, j, 3) and # There are enough spaces for a boat
                    state.board.boat_available(i,j,'Begin') and # All positions are available
                    state.board.boat_available(i,j+1,'Middle') and
                    state.board.boat_available(i,j+2,'End')):
                    action = Action(3, ((i,j),(i,j+1),(i,j+2)), HORIZONTAL )
                    if(self.result(state, action).board.verify_lines()):
                        actionList.append(action)

        # Try to find spots for 2-boat
        for i in range(0,9): #searching downwards orientation, starting at [i,j]
            for j in range(0,10):
                if (state.board.enough_space('Column', i, j, 2) and # There are enough spaces for a boat
                    state.board.boat_available(i,j,'Begin') and # All position are available
                    state.board.boat_available(i+1,j,'End')):
                    action = Action(2, ((i,j),(i+1,j)), VERTICAL )
                    if(self.result(state, action).board.verify_lines()):
                        actionList.append(Action(2, ((i,j),(i+1,j)), VERTICAL ))
        for i in range(0,10): #searching rightwards orientation, starting at [i,j]
            for j in range(0,9):
                if (state.board.enough_space('Row', i, j, 2) and # There are enough spaces for a boat
                    state.board.boat_available(i,j,'Begin') and # All positions are available
                    state.board.boat_available(i,j+1,'End')):
                    action = Action(2, ((i,j),(i,j+1)), HORIZONTAL )
                    if(self.result(state, action).board.verify_lines()):
                        actionList.append(action)
        
        # Try to find spots for 1-boat
        for i in range(0,10): 
            for j in range(0,10):
                if (state.board.board_matrix[i][j] == EMPTY and #Empty
                    not state.board.isBlockedBoat(i,j) and #Not blocked
                    not state.board.rows[i].fullBoat() and #Row not full
                    not state.board.columns[j].fullBoat()): #Column not full
                  action = Action(1, (i,j), VERTICAL)
                  if(self.result(state, action).board.verify_lines()):
                    actionList.append(Action(1, (i,j), VERTICAL))
        return list(reversed(actionList))
    
    def result(self, state_original: BimaruState, action: Action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        #print("Using Action: " + str(action.type) + str(action.value))
        state = copy.deepcopy(state_original)
        state.board = copy.deepcopy(state_original.board)
        state.board.board_matrix = copy.deepcopy(state_original.board.board_matrix)
        state.board.rows = copy.deepcopy(state_original.board.rows)
        state.board.columns = copy.deepcopy(state_original.board.columns)
        state.board.placed_boats = copy.deepcopy(state_original.board.placed_boats)
        state.board.placed_waters = copy.deepcopy(state_original.board.placed_waters)
        if(action.boat_size == 4):
            if(action.orientation == VERTICAL):
                x = action.coordinates[0][0]
                y = action.coordinates[0][1]
                state.board.set_value(x,y,UP)
                state.board.put_water_up(x,y)
                state.board.put_water_horizontal(x,y)
                x = action.coordinates[1][0]
                y = action.coordinates[1][1]
                state.board.set_value(x,y,MID)
                state.board.put_water_horizontal(x,y)
                x = action.coordinates[2][0]
                y = action.coordinates[2][1]
                state.board.set_value(x,y,MID)
                state.board.put_water_horizontal(x,y)
                x = action.coordinates[3][0]
                y = action.coordinates[3][1]
                state.board.set_value(x,y,DOWN)
                state.board.put_water_down(x,y)
                state.board.put_water_horizontal(x,y)
            elif(action.orientation == HORIZONTAL):
                x = action.coordinates[0][0]
                y = action.coordinates[0][1]
                state.board.set_value(x,y,LEFT)
                state.board.put_water_left(x,y)
                state.board.put_water_vertical(x,y)
                x = action.coordinates[1][0]
                y = action.coordinates[1][1]
                state.board.set_value(x,y,MID)
                state.board.put_water_vertical(x,y)
                x = action.coordinates[2][0]
                y = action.coordinates[2][1]
                state.board.set_value(x,y,MID)
                state.board.put_water_vertical(x,y)
                x = action.coordinates[3][0]
                y = action.coordinates[3][1]
                state.board.set_value(x,y,RIGHT)
                state.board.put_water_right(x,y)
                state.board.put_water_vertical(x,y)
        elif(action.boat_size == 3):
            if(action.orientation == VERTICAL):
                x = action.coordinates[0][0]
                y = action.coordinates[0][1]
                state.board.set_value(x,y,UP)
                state.board.put_water_up(x,y)
                state.board.put_water_horizontal(x,y)
                x = action.coordinates[1][0]
                y = action.coordinates[1][1]
                state.board.set_value(x,y,MID)
                state.board.put_water_horizontal(x,y)
                x = action.coordinates[2][0]
                y = action.coordinates[2][1]
                state.board.set_value(x,y,DOWN)
                state.board.put_water_down(x,y)
                state.board.put_water_horizontal(x,y)
            elif(action.orientation == HORIZONTAL):
                x = action.coordinates[0][0]
                y = action.coordinates[0][1]
                state.board.set_value(x,y,LEFT)
                state.board.put_water_left(x,y)
                state.board.put_water_vertical(x,y)
                x = action.coordinates[1][0]
                y = action.coordinates[1][1]
                state.board.set_value(x,y,MID)
                state.board.put_water_vertical(x,y)
                x = action.coordinates[2][0]
                y = action.coordinates[2][1]
                state.board.set_value(x,y,RIGHT)
                state.board.put_water_right(x,y)
                state.board.put_water_vertical(x,y)
        elif(action.boat_size == 2):
            if(action.orientation == VERTICAL):
                x = action.coordinates[0][0]
                y = action.coordinates[0][1]
                state.board.set_value(x,y,UP)
                state.board.put_water_up(x,y)
                state.board.put_water_horizontal(x,y)
                x = action.coordinates[1][0]
                y = action.coordinates[1][1]
                state.board.set_value(x,y,DOWN)
                state.board.put_water_down(x,y)
                state.board.put_water_horizontal(x,y)
            elif(action.orientation == HORIZONTAL):
                x = action.coordinates[0][0]
                y = action.coordinates[0][1]
                state.board.set_value(x,y,LEFT)
                state.board.put_water_left(x,y)
                state.board.put_water_vertical(x,y)
                x = action.coordinates[1][0]
                y = action.coordinates[1][1]
                state.board.set_value(x,y,RIGHT)
                state.board.put_water_right(x,y)
                state.board.put_water_vertical(x,y)
        elif(action.boat_size == 1):
            x = action.coordinates[0]
            y = action.coordinates[1]
            state.board.set_value(x,y,CENTER)
            state.board.put_water_horizontal(x,y)
            state.board.put_water_vertical(x,y)
        for i in range(0,10):
            if(state.board.rows[i].fullBoat()):
                for j in range(0,10):
                    if(state.board.board_matrix[i][j] == EMPTY):
                        state.board.set_value(i,j,WATER)
            if(state.board.columns[i].fullBoat()):
                for j in range(0,10):
                    if(state.board.board_matrix[j][i] == EMPTY):
                        state.board.set_value(j,i,WATER)
        return state
            
    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        #print("Goal Test: "+ str(state.board.placed_waters + state.board.placed_boats))
        if(not state.board.verify_lines()):
            return False
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

    goal_node = depth_first_tree_search(bimaru)
    print("Is goal?", bimaru.goal_test(goal_node.state))
    print("Solution:\n", goal_node.state.board.print2(), sep="")

    for action in bimaru.actions(goal_node.state):
        print(action.toString())