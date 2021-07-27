import itertools
import cspbase

from propagators import *
from futoshiki_csp import *

def test_board3():
    board_3 = [[4,'.',0,'<',0,'.',0,'.',0,'<',5],[0,'>',0,'<',6,'.',0,'.',0,'<',0],[0,'<',0,'.',0,'>',0,'<',0,'.',0], [6,'.',0,'.',0,'.',0,'<',0,'.',0],[0,'<',0,'<',0,'.',0,'.',0,'.',4],[0,'.',0,'>',0,'<',0,'.',4,'<',0]]
    #1st model test
    csp, var_array = futoshiki_csp_model_1(board_3)
    if csp is None:
        print("Failed first model test: wrong solution")
    else:
        solver = BT(csp)
        solver.bt_search(prop_GAC, var_ord=None)
        sol = []
        for i in range(len(var_array)):
            for j in range(len(var_array)):
                sol.append(var_array[i][j].get_assigned_value())

test_board3()