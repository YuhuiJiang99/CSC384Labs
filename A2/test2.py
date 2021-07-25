def compute_heuristic(state, color): 
    # IMPLEMENT
    stage = game_stage(state, color)
    if stage == "mid-game":
        return piece_and_row_heur(state, color)
    elif stage == "early-game":
        return compute_utility(state, color)
    return sum_to_distance_heur(state, color)  # change this!
def piece_and_row_heur(state, color):
    util = 0
    oppColor = OppDic1[color]
    for i in range(0, len(state.board)-1):
        for j in range(0, len(state.board[0])-1):
            cell = state.board[i][j]
            if cell is not None:
                if cell == color or cell == color.upper():
                    isKing = False
                    if cell == color.upper():
                        isKing = True
                    util += 5 + j + 2 * isKing
                elif cell == oppColor or cell == oppColor.upper():
                    isKing = False
                    if cell == oppColor.upper():
                        isKing = True
                    util -= 5 + (8 - j) + 2 * isKing
    
    return util
def piece_and_board_heur(state, color):
    oppColor = OppDic1[color]
    util = 0
    num_pieces = 0
    for i in range(0, len(state.board)-1):
        for j in range(0, len(state.board[0])-1):
            cell = state.board[i][j]
            if cell is not None:
                num_pieces += 1
                if cell == color.upper():
                    util += 10
                elif cell == oppColor.upper():
                    util -= 10
                elif cell == color and j < 4:
                    util += 5
                elif cell == oppColor and j < 4:
                    util -= 7
                elif cell == color and j >= 4:
                    util += 7
                elif cell == oppColor and j >= 4:
                    util -= 5
    #return util / num_pieces
    return util 
def pieces_location(state, color):
    oppColor = OppDic1[color]
    color_pieces = []
    oppColor_pieces = []
    for i in range(0, len(state.board)-1):
        for j in range(0, len(state.board[0])-1):
            cell = state.board[i][j]
            if cell is not None:
                if cell == color or cell == color.upper():
                    color_pieces.append((i,j))
                elif cell == oppColor or cell == oppColor.upper():
                    oppColor_pieces.append((i,j))
    return color_pieces, oppColor_pieces
def sum_to_distance_heur(state, color):
    util = 0
    color_pieces, oppColor_pieces = pieces_location(state, color)
    for c in color_pieces:
        for oc in oppColor_pieces:
            util += math.sqrt((c[0] - oc[0])**2 + (c[1] - oc[1])**2)
    
    if len(color_pieces) >= len(oppColor_pieces):
        util *= -1
    return util
def game_stage(state, color):
    oppColor = OppDic1[color]
    #Checks if all Kings
    for i in state.board:
        for j in i:
            if j in PlayerDic[color] or j in OppDic[oppColor]:
                if j != color.upper() and j != oppColor.upper():
                    return "mid-game"
    return "end-game"