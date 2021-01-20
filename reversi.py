# coding: utf-8
#
# reversi.py
#
#            Copyright (C) 2021 Keisuke Ueda
#
import time
import numpy as np

# The size of board
SIZE = 8
# The start condition
START_BOARD = np.zeros((SIZE, SIZE), dtype=int)
START_BOARD[SIZE//2, SIZE//2], START_BOARD[SIZE//2-1, SIZE//2-1] = 1, 1
START_BOARD[SIZE//2-1, SIZE//2], START_BOARD[SIZE//2, SIZE//2-1] = -1, -1
# The maximum serch depth of Min-Max method
DEPTH = 3


class Game:
    # First player: -1, Second player: 1
    def __init__(self, b, first_eb, second_eb):
        self.board = b
        self.eboards = (first_eb, np.nan, second_eb)
    
    
    # Copy this class itself
    def copy(self):
        return Game(self.board.copy(), self.eboards[0], self.eboards[2])
    
    
    # Count the number of player's stones.
    def count_stones(self, player):
        return np.sum(self.board == player)
    
    
    # Find the positions where the player can put a stone.
    #   arg:    player
    #   return: pos
    def find_available(self, player):
        availables = []
        for x in range(SIZE):
            for y in range(SIZE):
                if self.board[x,y] == 0:
                    if np.sum(self.board != self.forward(player, (x,y))) > 1:
                        availables.append((x,y))
        return availables
    
    
    # Judge if the game has ended.
    def judge_gameend(self):
        if np.sum(START_BOARD==0) == 0:
            return True
        elif (not self.find_available(1)) and (not self.find_available(-1)):
            return True
        else:
            return False
    
    
    # Judge the winner of this game
    # if draw, return 0
    def judge_winner(self):
        # 先手、後手の石の数
        num_1, num_2 = self.count_stones(-1), self.count_stones(1)
        if num_1 > num_2: return -1
        elif num_1 < num_2 : return 1
        else: return 0
        
        
    # Put a stone on a specific position.
    #   arg:    player, position
    #   return: board
    def forward(self, player, pos):
        b = self.board.copy()
        b[pos] = player
        # Search in eight directions
        for i in (-1,0,1):
            for j in (-1,0,1):
                if (i==0 and j==0): continue
                # Search until the condition is satisfied
                for k in range(1,SIZE):
                    x, y = pos[0]+i*k, pos[1]+j*k
                    # Judge if the position is inside the board
                    if (x not in np.arange(0,SIZE)) or (y not in np.arange(0,SIZE)): break
                    if (self.board[x,y]==0): break
                    if (self.board[x,y]==player):
                        for l in range(1,k): b[pos[0]+i*l, pos[1]+j*l] = player
                        break
        return b
    
    
    # The board-evaluation function for the player
    #   arg:    player
    #   return: evaluation score for the player
    def eval_board(self, player):
        eb = self.eboards[player+1]
        return np.sum(eb * self.board) * player
    
    
    # Min-Max methods
    #   arg:    game, evaluator(first player), player, max-search-depth, threshold to cutoff
    #   return: evaluation score, success of positions to take
    def minmax(self, evaluator, player, depth, limit):
        if depth == 0:
            return self.eval_board(evaluator), []

        switch = 1 if evaluator==player else -1
        value = -switch * np.inf
        choices = self.find_available(player)

        # When choices have no content
        if not choices:
            return self.eval_board(evaluator), []

        move = []
        for pos in choices:
            g = self.copy()
            g.board = g.forward(player, pos)
            v, m = g.minmax(evaluator, -player, depth-1, value)
            # min-max method (if switch=-1 -> value=min, switch=1 -> value=max)
            if value * switch < v * switch:
                value = v
                move = m + [pos]
            # alpha-beta method (The debug cannot be completed)
            #if value * switch >= limit * switch: break
        return value, move

    
    # find best move
    #   arg:    game, player(1 or -1), depth
    #   return: score, best move
    def find_best_move(self, player, depth):
        result = self.minmax(player, player, depth, np.inf)
        try:
            score, best_move = result[0], result[1][-1]
        except:
            print(result)
        return score, best_move
    
    
    def player_action(self, player):
        # 石がまだ置ける時
        if self.find_available(player):
            evaluation = self.find_best_move(player, DEPTH)
            self.board = self.forward(player, evaluation[1])
            return "Move: {}, Score: {}".format(evaluation[1], evaluation[0])
        else:
            return "----- No Choices -----"
    

    def plot_board(self):
        for x in range(SIZE):
            for y in range(SIZE):
                s = self.board[x,y]
                if s==1: print('●', end='')
                elif s==-1: print('○', end='')
                else: print('-', end='')
            print()

            
            
# play game without display
#   arg:    The first player's evaluation func., the second player's evaluation func.
#   return: the winner
def play(first_eb, second_eb, debug_mode):
    start = time.time()
    game = Game(START_BOARD.copy(), first_eb, second_eb)
    # -1が先手
    player = -1
    while not game.judge_gameend():
        board = game.board.copy()
        _ = game.player_action(player)
        player *= -1
    end = time.time()
    if debug_mode:
        game.plot_board()
        print("time: {:3.1f} seconds".format(end-start))
    return game.judge_winner()
     

# Play game with display
#   arg:    The first player's evaluation func., the second player's evaluation func.
#   return: 
def play_usermode(first_eb, second_eb):
    print("----------------------")
    print("----- Game Start -----")
    print("----------------------")
    print("first: Player(-1), second: Player(1)")
    print()
    start = time.time()
    game = Game(START_BOARD.copy(), first_eb, second_eb)
    game.plot_board()
    # -1が先手
    player = -1
    while not game.judge_gameend():
        board = game.board.copy()
        print(game.player_action(player))
        game.plot_board()
        player *= -1
    end = time.time()
    print()
    print("--------------------")
    print("----- Game End -----")
    print("--------------------")
    print("time: {:3.1f} seconds".format(end-start))
    winner = game.judge_winner()
    if winner: print("The winner: Player({})".format(winner))
    else: print("This game is Draw")