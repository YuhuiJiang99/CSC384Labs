#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files
import math
import os #for time functions
import csv
from search import * #for search engines
from sokoban import SokobanState, Direction, PROBLEMS #for Sokoban specific classes and problems
preval = 0
def sokoban_goal_state(state):
    '''
    @return: Whether all boxes are stored.
    '''
    for box in state.boxes:
        if box not in state.storage:
            return False
    return True

def min_manhattan_distance(box, arr):
    mindis = float('inf')
    for ele in arr:
        dis = abs(box[0]-ele[0]) + abs(box[1]-ele[1])
        if dis < mindis:
            mindis = dis 
    return mindis

def heur_manhattan_distance(state):
    #IMPLEMENT
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    #We want an admissible heuristic, which is an optimistic heuristic.
    #It must never overestimate the cost to get from the current state to the goal.
    #The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it is such a heuristic.
    #When calculating distances, assume there are no obstacles on the grid.
    #You should implement this heuristic function exactly, even if it is tempting to improve it.
    #Your function should return a numeric value; this is the estimate of the distance to the goal.
    sumMahD = 0
    for box in state.boxes:
        if box not in state.storage:
            sumMahD += min_manhattan_distance(box, state.storage)
    return sumMahD

#SOKOBAN HEURISTICS
def trivial_heuristic(state):
    '''trivial admissible sokoban heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state (# of moves required to get) to the goal.'''
    count = 0
    for box in state.boxes:
        if box not in state.storage:
            count += 1
    return count

#Check if a box is in a corner formed by wall/obstacles
def cornerDL(state, box):
    upBlock = (box[1] <= 0) or ((box[0], box[1] - 1) in state.obstacles)
    downBlock =  (box[1] >= state.height-1) or ((box[0], box[1] + 1) in state.obstacles)
    leftBlock = (box[0] <= 0) or ((box[0]-1, box[1]) in state.obstacles)
    rightBlock = (box[0] >= state.width-1) or ((box[0]+1, box[1]) in state.obstacles)
    return (upBlock or downBlock) and (leftBlock or rightBlock) 

#Check if a box is along a wall and there is no storage in that line
def edgeDL(state, box):
    upBlock = (box[1] <= 0)
    downBlock = (box[1] >= state.height-1)
    leftBlock = (box[0] <= 0)
    rightBlock = (box[0] >= state.width-1)
    if upBlock or downBlock: #check if the box hit top or bottom wall
        return not any([box[1]==storage[1] for storage in state.storage]) #if no storage is along the top/bottom wall, then there is a edge DL
    elif leftBlock or rightBlock: #check if the box hit left or right wall
        return not any([box[0]==storage[0] for storage in state.storage])#if no storage is along the left/right wall, then there is a edge DL
    else:
        return False #not encounter edge DL

#Check if there are at least 2 consecutive box along a wall
def wallConsecDL(state, box):
    upBlock = (box[1] <= 0)
    downBlock = (box[1] >= state.height-1)
    leftBlock = (box[0] <= 0)
    rightBlock = (box[0] >= state.width-1)

    boxUp = ((box[0], box[1]-1) in state.boxes)
    boxDown = ((box[0], box[1]+1) in state.boxes)
    boxLeft = ((box[0]-1, box[1]) in state.boxes)
    boxRight = ((box[0]+1, box[1]) in state.boxes)
    if (upBlock or downBlock) and (boxLeft or boxRight):
        return True 
    elif (leftBlock or rightBlock) and (boxUp or boxDown):
        return True 
    else:
        return False    

#Check if there are at least 2 consecutive box along obstacles
#It's not used in the heur_alt since there are few cases for this deadlock and it can't help increase the number of solved problems.
#So it's not worth to spend additional time to check this deadlock
def obsConsecDL(state, box):
    upBlock = ((box[0], box[1]-1) in state.obstacles) or ((box[0], box[1]-1) in state.boxes)
    downBlock = ((box[0], box[1]+1) in state.obstacles) or ((box[0], box[1]+1) in state.boxes)
    leftBlock = ((box[0]-1, box[1]) in state.obstacles)  or ((box[0]-1, box[1]) in state.boxes)
    rightBlock = ((box[0]+1, box[1]) in state.obstacles) or ((box[0]+1, box[1]) in state.boxes)

    boxUp = ((box[0], box[1]-1) in state.boxes)
    boxDown = ((box[0], box[1]+1) in state.boxes)
    boxLeft = ((box[0]-1, box[1]) in state.boxes)
    boxRight = ((box[0]+1, box[1]) in state.boxes)

    obsUpLeft = ((box[0]-1, box[1]-1) in state.obstacles) or ((box[0]-1, box[1]-1) in state.boxes)
    obsUpRight = ((box[0]+1, box[1]-1) in state.obstacles) or ((box[0]+1, box[1]-1) in state.boxes)
    obsDownLeft = ((box[0]-1, box[1]+1) in state.obstacles) or ((box[0]-1, box[1]+1) in state.boxes)
    obsDownRight = ((box[0]+1, box[1]+1) in state.obstacles) or ((box[0]+1, box[1]+1) in state.boxes)

    if upBlock:
        return (boxLeft and obsUpLeft) or (boxRight and obsUpRight)
    elif downBlock:
        return (boxLeft and obsDownLeft) or (boxRight and obsDownRight)
    elif leftBlock:
        return (boxUp and obsUpLeft) or (boxDown and obsDownLeft)
    elif rightBlock:
        return (boxUp and obsUpRight) or (boxDown and obsDownRight)
    else:
        return False

def storageDL(state, storage):
    upBlock = storage[1] <= 0 or ((storage[0], storage[1]-1) in state.boxes and (storage[0], storage[1]-2) in state.boxes)
    downBlock = storage[1] >= state.height-1 or ((storage[0], storage[1]+1) in state.boxes and (storage[0], storage[1]+2) in state.boxes)
    leftBlock = storage[0] <= 0 or ((storage[0]-1, storage[1]) in state.boxes and (storage[0]-2, storage[1]) in state.boxes)
    rightBlock = storage[0] >= state.width-1 or ((storage[0]+1, storage[1]) in state.boxes and (storage[0]+2, storage[1]) in state.boxes)
    return upBlock and downBlock and leftBlock and rightBlock

def heur_alternate(state):
    #IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    #heur_manhattan_distance has flaws.
    #Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    #Your function should return a numeric value for the estimate of the distance to the goal.

    #1. New manhattan distance caculation:
        #As mentioned in the a1 instruction, heur_manhattan_distance(state) only consider the manhattan distance of every box 
        #to the nearest storage point. In my heur_alt function, I also take the distance of every box
        #to the nearest robot into account. Besides, I only consider the unoccupied storage point as the set for the unstored box
        #to select from.
    #2. Deadlock detection:
        #In sokoban problems, a deadlock happened when a state become unsolvable at all. In our assignment, a robot can only 
        #PUSH ONE box at one time. Under these conditions, I implemented some basic deadlock detections:
        #(1) Corner Deadlock: There is at least one unstored box located at a corner formed by either walls or obstacles.
        #(2) Edge Deadlock: There is at least one unstored box located along the wall and there is no storage point along that wall.
        #(3) Consecutive Box Deadlock: At least two unstored boxes are put consecutively along a wall/obstacles
    #3. Previous manhattan distance(for saving time):
        #To find the manhattan distance of a single state takes some time: O(n^2). Also, I noticed that some states have the same box locations 
        #with their parents' box location because a robot just moves a space and doesn't push any box. Under these cases, we can save some
        #running time by just remembering the manhattan distance of the boxes to storages in the last state and use it to calculate the 
        #heuristic of the new state.
    global preval
    if state.parent and state.parent.boxes == state.boxes:
        hval = preval
        if hval == float('inf'):
            return float('inf') 
        for box in state.boxes:
            if box not in state.storage:
                hval += min_manhattan_distance(box, state.robots)
    else:
        preval = 0
        hval = 0
        unpickedStorages = set()
        for storage in state.storage:
            if storage not in state.boxes:
                unpickedStorages.add(storage)
        for box in state.boxes:
            if box not in state.storage:
                if cornerDL(state, box) or edgeDL(state, box) or wallConsecDL(state, box):                  
                    preval = float('inf')
                    return float('inf')
                #Find min manh distance between storages and box 
                minStorMahDis = min_manhattan_distance(box, unpickedStorages)
                hval += minStorMahDis
                preval += minStorMahDis
                #Find min manh distance between robots and box 
                hval += min_manhattan_distance(box, state.robots)

    return hval

def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def standard_astar_fval(sN):
    return sN.gval + sN.hval

def fval_function(sN, weight):
    #IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.
    Use this function stub to encode the standard form of weighted A* (i.e. g + w*h)

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
  
    #Many searches will explore nodes (or states) that are ordered by their f-value.
    #For UCS, the fvalue is the same as the gval of the state. For best-first search, the fvalue is the hval of the state.
    #You can use this function to create an alternate f-value for states; this must be a function of the state and the weight.
    #The function must return a numeric f-value.
    #The value will determine your state's position on the Frontier list during a 'custom' search.
    #You must initialize your search engine object as a 'custom' search engine if you supply a custom fval function.
    return sN.gval + weight*sN.hval

def fval_function_XUP(sN, weight):
    #IMPLEMENT
    """
    Another custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.
    Use this function stub to encode the XUP form of weighted A* 

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    
    return (1/(2*weight))*(sN.gval + sN.hval + math.sqrt((sN.gval+sN.hval)**2 + 4*weight*(weight-1)*(sN.hval**2)))

def fval_function_XDP(sN, weight):
    #IMPLEMENT
    """
    A third custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.
    Use this function stub to encode the XDP form of weighted A* 

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return (1/(2*weight))*(sN.gval + (2*weight-1)*sN.hval + math.sqrt((sN.gval-sN.hval)**2 + 4*weight*sN.gval*sN.hval))

def compare_weighted_astars():
    #IMPLEMENT
    '''Compares various different implementations of A* that use different f-value functions'''
    '''INPUT: None'''
    '''OUTPUT: None'''
    """
    This function should generate a CSV file (comparison.csv) that contains statistics from
    4 varieties of A* search on 3 practice problems.  The four varieties of A* are as follows:
    Standard A* (Variant #1), Weighted A*  (Variant #2),  Weighted A* XUP (Variant #3) and Weighted A* XDP  (Variant #4).  
    Format each line in your your output CSV file as follows:

    A,B,C,D,E,F

    where
    A is the number of the problem being solved (0,1 or 2)
    B is the A* variant being used (1,2,3 or 4)
    C is the weight being used (2,3,4 or 5)
    D is the number of paths extracted from the Frontier (or expanded) during the search
    E is the number of paths generated by the successor function during the search
    F is the overall solution cost    

    Note that you will submit your CSV file (comparison.csv) with your code
    """
    header = ['Problem', 'A* Variant', 'Weight', 'Expanded Paths', 'Generated Paths', 'Overall Solution Cost']
    data = []
    
    for i in range(0,3):
        problem = PROBLEMS[i] 
        for AV in range(1,5):
            if AV == 1:
                se = SearchEngine('astar', 'default')
                se.init_search(problem, sokoban_goal_state, heur_manhattan_distance)
                goal_state, stats = se.search()
                if goal_state:
                    data.append([i, AV, "N/A", stats.states_expanded, stats.states_generated, goal_state.gval])
                else:
                    data.append([i, AV, None, None, None, None])
            else: 
                se = SearchEngine('custom', 'default')
                for weight in [2,3,4,5]:
                    #you can write code in here if you like
                    if AV == 2:
                        wrapped_fval_function = (lambda sN : fval_function(sN, weight))
                    elif AV == 3:
                        wrapped_fval_function = (lambda sN : fval_function_XUP(sN, weight))
                    elif AV == 4:
                        wrapped_fval_function = (lambda sN : fval_function_XDP(sN, weight))
                    
                    se.init_search(problem, sokoban_goal_state, heur_manhattan_distance, wrapped_fval_function)
                    goal_state, stats = se.search()
                    if goal_state:
                        data.append([i, AV, weight, stats.states_expanded, stats.states_generated, goal_state.gval])
                    else:
                        data.append([i, AV, weight, None, None, None])
 
    with open('comparison.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)

def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
    #IMPLEMENT
    '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of weighted astar algorithm'''
    #Initialize search engine
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))
    se = SearchEngine('custom', 'default')
    se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)
    #Initialize cost bound and time bound
    ret_state = False
    costBound = None
    curTime = os.times()[0]
    endTime = curTime + timebound 

    while curTime < endTime:
        goal_state = se.search(endTime-curTime, costBound)[0]
        if goal_state == False:
            break  #Directly break looping here since if we can't find better solution under current cost bound, then we can'f find with lower cost bound
        ret_state = goal_state #Update the optimal solution to be current solution
        costBound = (goal_state.gval, float('inf'), goal_state.gval)#Update the costbound to be current solution gval
        curTime = os.times()[0] #Update current time
        if weight > 1:
            weight -= 0.5 #Update the weight
    return ret_state

def anytime_gbfs(initial_state, heur_fn, timebound = 10):
    #IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of anytime greedy best-first search'''    
    #Initialize search engine
    se = SearchEngine('best_first', 'default')
    se.init_search(initial_state, sokoban_goal_state, heur_fn)
    #Initialize cost bound and time bound
    ret_state = False
    costBound = None
    curTime = os.times()[0]
    endTime = curTime + timebound
    while curTime < endTime:
        goal_state = se.search(endTime-curTime, costBound)[0]
        if goal_state == False:
            break   #Directly break looping here since if we can't find better solution under current cost bound, then we can'f find with lower cost bound
        ret_state = goal_state #Update the optimal solution to be current solution
        costBound = (goal_state.gval, float('inf'), float('inf'))#Update the costbound to be current solution gval
        curTime = os.times()[0] #Update current time
    return ret_state

print("hello")