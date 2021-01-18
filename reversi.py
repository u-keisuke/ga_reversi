# coding: utf-8
#
# reversi.py
#
#            Copyright (C) 2021 Keisuke Ueda
#
import time
import numpy as np


SIZE = 8
START_BOARD = np.zeros((SIZE, SIZE), dtype=int)
START_BOARD[SIZE//2, SIZE//2], START_BOARD[SIZE//2-1, SIZE//2-1] = 1, 1
START_BOARD[SIZE//2-1, SIZE//2], START_BOARD[SIZE//2, SIZE//2-1] = -1, -1
DEPTH = 3


class Game:
    # -1が先攻、1が後攻
    def __init__(self, b, first_eb, second_eb):
        self.board = b
        self.eboards = (first_eb, np.nan, second_eb)
    
    
    def copy(self):
        return Game(self.board.copy(), self.eboards[0], self.eboards[2])
    
    
    def count_stones(self, player):
        return np.sum(self.board == player)
    
    
    # 石が置けるところを探す
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
    
    
    def judge_gameend(self):
        if np.sum(START_BOARD==0) == 0:
            return True
        elif (not self.find_available(1)) and (not self.find_available(-1)):
            return True
        else:
            return False
    
    
    # if draw, return 0
    def judge_winner(self):
        # 先手、後手の石の数
        num_1, num_2 = self.count_stones(-1), self.count_stones(1)
        if num_1 > num_2: return -1
        elif num_1 < num_2 : return 1
        else: return 0
        
    
    # playerがposに石を置く
    def forward(self, player, pos):
        b = self.board.copy()
        b[pos] = player
        # 8方向に探索
        for i in (-1,0,1):
            for j in (-1,0,1):
                if (i==0 and j==0): continue
                # focusしている部分が条件を満たすまで探索
                for k in range(1,SIZE):
                    x, y = pos[0]+i*k, pos[1]+j*k
                    # 盤面の範囲内かどうか
                    if (x not in np.arange(0,SIZE)) or (y not in np.arange(0,SIZE)): break
                    if (self.board[x,y]==0): break
                    if (self.board[x,y]==player):
                        for l in range(1,k): b[pos[0]+i*l, pos[1]+j*l] = player
                        break
        return b
    
    
    # playerにとっての盤面評価関数
    def eval_board(self, player):
        eb = self.eboards[player+1]
        return np.sum(eb * self.board) * player
    
    
    # alpha-beta methods
    #   arg:    game, evaluator(先手), player, 探索の深さ, 枝刈り用の閾値
    #   return: 盤面の評価値, 置いた石のpos
    def alphabeta(self, evaluator, player, depth, limit):
        if depth == 0:
            return self.eval_board(evaluator), []

        # playerが先手なら1, 後手なら-1
        switch = 1 if evaluator==player else -1
        value = -switch * np.inf
        choices = self.find_available(player)

        # choicesが空のリストの場合
        if not choices:
            return self.eval_board(evaluator), []

        move = []
        for pos in choices:
            g = self.copy()
            g.board = g.forward(player, pos)
            v, m = g.alphabeta(evaluator, -player, depth-1, value)
            # min-max method (if switch=-1 -> value=min, switch=1 -> value=max)
            if value * switch < v * switch:
                value = v
                move = m + [pos]
            # alpha-beta method
            #if value * switch >= limit * switch: break
        return value, move

    
    
    # find best move
    #   arg:    game, player(1 or -1), depth
    #   return: score, best move
    def find_best_move(self, player, depth):
        result = self.alphabeta(player, player, depth, np.inf)
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

        


# play game
#   arg:    先手のagentの評価盤面, 後手の評価盤面
#   return: 
def play(first_eb, second_eb):
    start = time.time()
    game = Game(START_BOARD.copy(), first_eb, second_eb)
    # -1が先手
    player = -1
    while not game.judge_gameend():
        board = game.board.copy()
        _ = game.player_action(player)
        player *= -1
    game.plot_board()
    end = time.time()
    print("time: {:3.1f} seconds".format(end-start))
    return game.judge_winner()
     

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