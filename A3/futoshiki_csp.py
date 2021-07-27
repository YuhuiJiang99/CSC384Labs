#Look for #IMPLEMENT tags in this file.
'''
All models need to return a CSP object, and a list of lists of Variable objects 
representing the board. The returned list of lists is used to access the 
solution. 

For example, after these three lines of code

    csp, var_array = futoshiki_csp_model_1(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the Futoshiki puzzle.

1. futoshiki_csp_model_1 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only 
      binary not-equal constraints for both the row and column constraints.

2. futoshiki_csp_model_2 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only n-ary 
      all-different constraints for both the row and column constraints. 

'''
from cspbase import *
import itertools
def futoshiki_csp_model_1(futo_grid):
    ##IMPLEMENT
    csp = None
    var_matrix = []
    csp_vars = []
    cons = [] 
    height = len(futo_grid)
    width = len(futo_grid[0])
    init_dom = [i for i in range(1, height+1)]

    #Create and append all variables in the futo_grid into var_matrix
    for i in range(0, height):
        vars_row = []
        for j in range(0, width, 2):
            if futo_grid[i][j] == 0:
                var = Variable(f"Var{i}{j//2}", init_dom)      
            else:
                var = Variable(f"Var{i}{j//2}", [futo_grid[i][j]])
                var.assign(futo_grid[i][j])
            vars_row.append(var)
            csp_vars.append(var)
        var_matrix.append(vars_row)
    

    #Create and append all constraints in the futo_grid into cons
    for i in range(0, height):
        for j in range(0, height):
            for k in range(j+1, height):
                var1 = var_matrix[i][j]
                dom1 = var1.cur_domain()
                var2 = var_matrix[i][k]
                dom2 = var2.cur_domain()
                con = Constraint(f"Con(Var{i}{j},Var{i}{k})", [var1, var2])
                if k == j+1:
                    binary_tups = create_binary_tuples(futo_grid[i][j*2+1], dom1, dom2)
                else:
                    binary_tups = create_binary_tuples('.', dom1, dom2)
                con.add_satisfying_tuples(binary_tups)
                cons.append(con)

                var1 = var_matrix[j][i]
                dom1 = var1.cur_domain()
                var2 = var_matrix[k][i]
                dom2 = var2.cur_domain()
                binary_tups = create_binary_tuples('.', dom1, dom2)
                con = Constraint(f"Con(Var{j}{i},Var{k}{i})", [var1, var2])
                con.add_satisfying_tuples(binary_tups)
                cons.append(con)
    csp_model1 = CSP(f"size {height} model 1 csp", csp_vars)
    for c in cons:  
        csp_model1.add_constraint(c)
    return csp_model1, var_matrix

def futoshiki_csp_model_2(futo_grid):
    ##IMPLEMENT
    csp = None
    var_matrix = []
    csp_vars = []
    cons = [] 
    height = len(futo_grid)
    width = len(futo_grid[0])
    init_dom = [i for i in range(1, height+1)]

    #Create and append all variables in the futo_grid into var_matrix
    for i in range(0, height):
        vars_row = []
        for j in range(0, width, 2):
            if futo_grid[i][j] == 0:
                var = Variable(f"Var{i}{j//2}", init_dom)      
            else:
                var = Variable(f"Var{i}{j//2}", [futo_grid[i][j]])
                var.assign(futo_grid[i][j])
            vars_row.append(var)
            csp_vars.append(var)
        var_matrix.append(vars_row)
    
    #Create and append all constraints in the futo_grid into cons
    for i in range(0, height):
        vars_row = []
        doms_row = []
        vars_col = []
        doms_col= []
        for j in range(0, height):
            vars_row.append(var_matrix[i][j])
            doms_row.append(var_matrix[i][j].cur_domain())
            vars_col.append(var_matrix[j][i])
            doms_col.append(var_matrix[j][i].cur_domain())
            if j < height-1 and futo_grid[i][j*2+1] != '.':
                var1 = var_matrix[i][j]
                dom1 = var1.cur_domain()
                var2 = var_matrix[i][j+1]
                dom2 = var2.cur_domain()
                binary_tups = create_binary_tuples(futo_grid[i][j*2+1], dom1, dom2)
                con = Constraint(f"Con(Var{i}{j},Var{i}{j+1})", [var1, var2])
                con.add_satisfying_tuples(binary_tups)
                cons.append(con)
        #Create and append row nary constraints to the constraints
        row_nary_tups = create_nary_tuples(doms_row)
        con = Constraint(f"Con(Row{i})", vars_row)
        con.add_satisfying_tuples(row_nary_tups)
        cons.append(con)

        #Create and append col nary constraints to the constraints
        col_nary_tups = create_nary_tuples(doms_col)
        con = Constraint(f"Con(Col{i})", vars_col)
        con.add_satisfying_tuples(col_nary_tups)
        cons.append(con)

    csp_model2 = CSP(f"size {height} model 2 futoshiki", csp_vars)
    for c in cons:
        csp_model2.add_constraint(c)

    return csp_model2, var_matrix

def create_binary_tuples(ineqOp, dom1, dom2):
    binary_tups = []
    for tup in itertools.product(dom1, dom2):
        if ineq(ineqOp, tup[0], tup[1]):
            binary_tups.append(tup)
    return binary_tups

def create_nary_tuples(doms):
    nary_tuples = []
    for tup in itertools.product(*doms):
        if len(tup) == len(set(tup)):
            nary_tuples.append(tup)
    return nary_tuples

def ineq(ineqOp, v1, v2):
    if ineqOp == '<':
        return v1 < v2
    elif ineqOp == '>':
        return v1 > v2
    else:
        return v1 != v2





   
# board_1 = [[1,'<',0,'.',0],[0,'.',0,'.',2],[2,'.',0,'>',0]]
# sp, var_array = futoshiki_csp_model_2(board_1)

