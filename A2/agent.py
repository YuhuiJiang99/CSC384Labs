from __future__ import nested_scopes
from checkers_game import *

#Heuristic function description
#In my opinion, there are two criteria to evaluate the heuristic function: 1. Goodness 2. Overhead cost.
#The goodness just means how much time sorting a level of node based on the heuritic value can save. 
#However in real time, we also need to consider about the addition running time cost the heuristic function 
#adds to the general procedure. I've tried many reasonable heuristic functions including number of moves,
#different game stage strategy, bonus of surrounding alliance, etc. However, after so many trials, I realized
#that the more complex the heuristic is, the harder for it to payoff its additional runtime cost.As a result,
#I decided to use a simple heuristic function simillar with the utility function to limit the time complexity to be
#under O(n^2), where n is the board length. The heuristic will weight more to kings and pieces on the edge where
#they can't be captured by opponents. In addition, as the depth gets deeper and the game search tree becomes larger, 
#sorting nodes adds more time cost. So, I decide to only run the node ordering in the top half of the search tree
#(current_layer> max_limit/2). When the depth limit is only 6 or 7, the program execution time is too fast for the 
#node ordering to show its advantage. While I increase the limit to 8-10, it has a visible effect on saving the runtime.


cache = {} #you can use this to implement state caching!
initCheckers = 0 
initial_limit = 0

# Method to compute utility value of terminal state
def compute_utility(state, color):
    value = 0
    oppColor = OppDic1[color]
    for row in state.board:
        for cell in row:
            if cell == color:
                value += 1
            elif cell == color.upper():
                value += 2
            elif cell == oppColor:
                value -= 1
            elif cell == oppColor.upper():
                value -= 2
    return value

def compute_heuristic(state, color):
    heur = 0
    oppColor = OppDic1[color]
    board = state.board
    length = len(board)
    color2score = {'r':1, 'b':1, 'R':2, 'B':2}
    #Check edge    
    for i in range(0, length):
        for j in range(0, length):
            cell = board[i][j]
            if cell in PlayerDic[color]:
                heur += color2score[cell]
                if i in [0, length-1] or j in [0, length-1]:
                    heur += color2score[cell]
            elif cell in PlayerDic[oppColor]:
                heur -= color2score[cell]
                if i in [0, length-1] or j in [0, length-1]:
                    heur -= color2score[cell]
    # heur += len(successors(state, color))
    return heur

#Defined but not used heuristics
def allianceBonus(i, j, board, color):
    bonus = 0
    for x in [-1, 1]:
        for y in [-1,1]:
            if board[i+x][j+y] in PlayerDic[color]:
                bonus += 1
    return bonus

#Defined but not used heuristics
def check_game_stage(state, color):
    global initCheckers
    playerCheckers = 0
    oppCheckers = 0
    oppColor = OppDic1[color]
    kings = 0
    for arr in state.board:
        for cell in arr:
            if cell in PlayerDic[color]:
                playerCheckers += 1
            elif cell in OppDic[color]:
                oppCheckers += 1
            if cell == color.upper() or oppColor.upper():
                kings += 1

    if playerCheckers <= 3 or oppCheckers <= 3:
        return 'end-game'
    elif kings > 0:
        return 'mid-game'
    else:
        return 'early-game'

############ MINIMAX ###############################
def minimax_min_node(state, color, limit, caching=0):
    # IMPLEMENT
    global cache
    tup = None
    if caching:
        tup = tuple(map(tuple, state.board))
        if (tup, color) in cache.keys():
            return cache[(tup, color)]

    nextStates = successors(state, color)
    if len(nextStates) == 0 or limit == 0:
        stopValue = compute_utility(state, OppDic1[color])
        if caching:
            cache[(tup, color)] = (stopValue, None)
        return stopValue, None
    else:
        minState = None
        minValue = float('inf')
        for nextState in nextStates:
            nextValue = minimax_max_node(nextState, OppDic1[color], limit-1, caching)[0]
            if nextValue < minValue:
                minValue, minState = nextValue, nextState 
        if caching:
            cache[(tup, color)] = (minValue, minState)
        return minValue, minState


def minimax_max_node(state, color, limit, caching=0):
    # IMPLEMENT
    global cache
    tup = None
    if caching:
        tup = tuple(map(tuple, state.board))
        if (tup, color) in cache.keys():
            return cache[(tup, color)]
    nextStates = successors(state, color)
    if len(nextStates) == 0 or limit == 0:
        stopValue = compute_utility(state, color)
        if caching:
            cache[(tup, color)] = (stopValue, None)
        return stopValue, None
    else:
        maxValue = float('-inf')
        maxState = None
        for nextState in nextStates:
            nextValue = minimax_min_node(nextState, OppDic1[color], limit-1, caching)[0]
            if nextValue > maxValue:
                maxValue, maxState = nextValue, nextState  
        if caching:
            cache[(tup, color)] = (maxValue, maxState)
        return maxValue, maxState


def select_move_minimax(state, color, limit, caching=0):
    """
        Given a state (of type Board) and a player color, decide on a move.
        The return value is a list of tuples [(i1,j1), (i2,j2)], where
        i1, j1 is the starting position of the piece to move
        and i2, j2 its destination.  Note that moves involving jumps will contain
        additional tuples.

        Note that other parameters are accepted by this function:
        If limit is a positive integer, your code should enforce a depth limit that is equal to the value of the parameter.
        Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
        value (see compute_utility)
        If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
        If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    """
    # IMPLEMENT
    global cache
    cache.clear()
    ret = minimax_max_node(state, color, limit, caching)
    if ret[1] is not None:
        return ret[1].move
    else:
        return None


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(state, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT
    global cache
    tup = None
    if caching:
        tup = tuple(map(tuple, state.board))
        if (tup, color) in cache.keys():
            return cache[(tup, color)]

    nextStates = successors(state, color)
    if len(nextStates) == 0  or limit == 0:
        stopValue = compute_utility(state, OppDic1[color])
        if caching:
            cache[(tup, color)] = (stopValue, None)
        return stopValue, None
    else:
        minValue = float('inf')
        minState = None
        if ordering and limit > (initial_limit//2):
            nextStates.sort(key=lambda x: compute_heuristic(x, OppDic1[color]))
        for nextState in nextStates:
            nextValue = alphabeta_max_node(nextState, OppDic1[color], alpha, beta, limit-1, caching, ordering)[0]
            if nextValue < minValue:
                minValue, minState = nextValue, nextState 
            if nextValue <= alpha:
                break
            beta = min(beta, nextValue)
        if caching:
            cache[(tup, color)] = (minValue, minState)
        return minValue, minState

def alphabeta_max_node(state, color, alpha, beta, limit, caching=0, ordering=0):
    # IMPLEMENT
    global cache
    tup = None
    if caching:
        tup = tuple(map(tuple, state.board))
        if (tup, color) in cache.keys():
            return cache[(tup, color)]

    nextStates = successors(state, color)
    if len(nextStates) == 0 or limit == 0:
        stopValue = compute_utility(state, color)
        if caching:
            cache[(tup, color)] = (stopValue, None)
        return stopValue, None
    else:
        maxValue = float('-inf')
        maxState = None
        if ordering and limit > (initial_limit//2):
            nextStates.sort(key=lambda x: compute_heuristic(x, color), reverse=True)
        for nextState in nextStates:
            nextValue = alphabeta_min_node(nextState, OppDic1[color], alpha, beta, limit-1, caching, ordering)[0]
            if nextValue > maxValue:
                maxValue, maxState = nextValue, nextState 
            if nextValue >= beta:
                break
            alpha = max(alpha, nextValue)
        if caching:
            cache[(tup, color)] = (maxValue, maxState)
        return maxValue, maxState


def select_move_alphabeta(state, color, limit, caching=0, ordering=0):
    """
    Given a state (of type Board) and a player color, decide on a move. 
    The return value is a list of tuples [(i1,j1), (i2,j2)], where
    i1, j1 is the starting position of the piece to move
    and i2, j2 its destination.  Note that moves involving jumps will contain
    additional tuples.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enforce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations. 
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations. 
    """
    # IMPLEMENT
    global cache
    cache.clear()
    global initial_limit
    initial_limit = limit
    ret = alphabeta_max_node(state, color, float('-inf'), float('inf'), limit, caching, ordering)
    if ret[1] is not None:
        return ret[1].move
    else:
        return None


# ======================== Class GameEngine =======================================
class GameEngine:
    def __init__(self, str_name):
        self.str = str_name

    def __str__(self):
        return self.str

    # The return value should be a move that is denoted by a list
    def nextMove(self, state, alphabeta, limit, caching, ordering):
        global PLAYER
        PLAYER = self.str
        if alphabeta:
            result = select_move_alphabeta(Board(state), PLAYER, limit, caching, ordering)
        else:
            result = select_move_minimax(Board(state), PLAYER, limit, caching)

        return result
