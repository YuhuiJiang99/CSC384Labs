import os #for time functions
from search import * #for search engines
from sokoban import SokobanState, Direction, PROBLEMS #for Sokoban specific classes and problems
import math
import csv
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
            shortestMahD = -1
            for storPoint in state.storage:
                tmpMahD = abs(box[0]-storPoint[0])+abs(box[1]-storPoint[1])
                if tmpMahD < shortestMahD or shortestMahD == -1:
                    shortestMahD = tmpMahD
            sumMahD += shortestMahD
    return sumMahD

def SDP(weight, gval, hval):
    ret1 = (1/(2*weight))*(gval + (2*weight-1)*hval + pow(math.sqrt(gval-hval), 2) + 4*weight*gval*hval)
    return ret1

def balance(weight, gval, hval):
    return gval + weight*hval

def SUP(weight, gval, hval):
    return (1/(2*weight))*(gval + hval + pow(math.sqrt(gval+hval),2) + 4*weight*(weight-1)*pow(hval, 2))

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
    header = ['Problem', 'A* Variant', 'Weight', 'Extracted Paths', 'Generated Paths', 'Overall Solution Cost']
    data = []
    for i in range(0,3): #
        problem = PROBLEMS[i] 
        for AV in range(1,5):
            for weight in [2,3,4,5]:
                #you can write code in here if you like
                data.append([i, AV, weight, 0, 0, 0])

    with open('comparison.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)

def getNumBlock(state, storage):
    numBlock = 0
    upBlock = storage[1] <= 0 or ((storage[0], storage[1]-1) in state.storage and (storage[0], storage[1]-1) in state.boxes)
    downBlock = storage[1] >= state.height-1 or ((storage[0], storage[1]+1) in state.storage and (storage[0], storage[1]+1) in state.boxes)
    leftBlock = storage[0] <= 0 or ((storage[0]-1, storage[1]) in state.storage and (storage[0]-1, storage[1]) in state.boxes)
    rightBlock = storage[0] >= state.width-1 or ((storage[0]+1, storage[1]) in state.storage and (storage[0]+1, storage[1]) in state.boxes)
    for block in [upBlock, downBlock, leftBlock, rightBlock]:
        if block:
            numBlock += 1
    return numBlock

def min_manhattan_distance(box, frozenSet):
    mindis = float('inf')
    tup = None
    for ele in frozenSet:
        dis = abs(box[0]-ele[0]) + abs(box[1]-ele[1])
        if dis < mindis:
            mindis = dis
            tup = ele
    return mindis,tup


def min_manhattan_distance2(box, frozenSet, dic):
    mindis = float('inf')
    tup = None
    for ele in frozenSet:
        dis = abs(box[0]-ele[0]) + abs(box[1]-ele[1]) + dic[ele]
        if dis < mindis:
            mindis = dis
            tup = ele
    return mindis, tup

def obsConsecDL(state, box):
    # Check if there are at least 2 consecutive box along obstacles
    # It's NOT used in the heur_alt since there are few cases for this deadlock and it can't help increase the number of solved problems.
    # So it's not worth to spend additional time to check this deadlock
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
    #Check if there is an empty storage surrounded by various blocks(walls, obstacles, filled storages)
    #It's NOT used in the heur_alt since there are few cases for this deadlock and it can't help increase the number of solved problems.
    #So it's not worth to spend additional time to check this deadlock
    upBlock = storage[1] <= 0 or ((storage[0], storage[1]-1) in state.boxes and (storage[0], storage[1]-2) in state.boxes)
    downBlock = storage[1] >= state.height-1 or ((storage[0], storage[1]+1) in state.boxes and (storage[0], storage[1]+2) in state.boxes)
    leftBlock = storage[0] <= 0 or ((storage[0]-1, storage[1]) in state.boxes and (storage[0]-2, storage[1]) in state.boxes)
    rightBlock = storage[0] >= state.width-1 or ((storage[0]+1, storage[1]) in state.boxes and (storage[0]+2, storage[1]) in state.boxes)
    return upBlock and downBlock and leftBlock and rightBlock

def min_corner_distance(storages, cornerSet):
    dic = dict()
    for storage in storages:
        minCornerDis = min([abs(storage[0]-corner[0]) + abs(storage[1]-corner[1]) for corner in cornerSet])
        dic[storage] = minCornerDis
    return dic

def set_storage_matrix(state):
    storageMatrix = dict()
    for storage in state.storage:
        upBlock = (storage[1] <= 0)
        downBlock = (storage[1] >= state.height-1)
        leftBlock = (storage[0] <= 0)
        rightBlock = (storage[0] >= state.width-1)
        if (upBlock or downBlock) and (leftBlock or rightBlock):
            storageMatrix[storage] = 100
        elif (upBlock or downBlock or leftBlock or rightBlock):
            storageMatrix[storage] = 10
        else:
            storageMatrix[storage] = 1
    return storageMatrix

# state = SokobanState("START", 0, None, 8, 8, # dimensions
#                  ((0, 5), (1, 6), (2, 7)), #robots
#                  frozenset(((6, 6), (1, 0), (4, 5), (0, 1), (1, 1), (5, 3))), #boxes
#                  frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2))), #storage
#                  frozenset() #obstacles
#                  )
# state.print_state()
# cornerSet = {(0,0), (0,7), (7,7), (7,0)}
# dic = min_corner_distance(state.storage, cornerSet)
# print(dic)
# cost = 0 
# unpickedStorages = set()
# for storage in state.storage:
#     if storage not in state.boxes:
#         # if storageDL(state,storage):
#         #     preval = float('inf')
#         #     return float('inf')
#         unpickedStorages.add(storage)
# print(sum([dic[storage] for storage in unpickedStorages]))

# unpickedStorage1 = set(p.storage)
# unpickedStorage2 = set(p.storage)
# print(dic)
# for box in p.boxes:
#     mindis1, tup1 = min_manhattan_distance(box, unpickedStorage1, dic)
#     mindis2, tup2 = min_manhattan_distance2(box, unpickedStorage2, dic)
#     unpickedStorage1.remove(tup1)
#     unpickedStorage2.remove(tup2)
#     print(f"1st method: Box {box} picked {tup1}")
#     print(f"2nd method: Box {box} picked {tup2}\n")


# s18 =   SokobanState("START", 0, None, 8, 8, # dimensions
#                  ((0, 5), (1, 6), (2, 7)), #robots
#                  frozenset(((0, 0), (1, 0), (5, 6), (0, 1), (1, 1), (6, 5))), #boxes
#                  frozenset(((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2))), #storage
#                  frozenset() #obstacles
#                  )
# s18.print_state()

# s = {1,3,5,7}
def checkBlockedState(state):
    numBlock = 0
    for storage in state.storage:
        if storage not in state.boxes:
            upBlock = storage[1] <= 0 or ((storage[0], storage[1]-1) in state.storage and (storage[0], storage[1]-1) in state.boxes)
            downBlock = storage[1] >= state.height-1 or ((storage[0], storage[1]+1) in state.storage and (storage[0], storage[1]+1) in state.boxes)
            leftBlock = storage[0] <= 0 or ((storage[0]-1, storage[1]) in state.storage and (storage[0]-1, storage[1]) in state.boxes)
            rightBlock = storage[0] >= state.width-1 or ((storage[0]+1, storage[1]) in state.storage and (storage[0]+1, storage[1]) in state.boxes)
            for block in [upBlock, downBlock, leftBlock, rightBlock]:
                if block:
                    numBlock += 1
            print(f"{storage}:{numBlock}")
    return numBlock 



a = {1,2,3}
b = {2,3,4}
print(a & b)
print(a - b)


n= 0
for p in PROBLEMS:
    print(f"Problem: {n}")
    p.print_state()
    n+=1

#For self testing
# if __name__ == '__main__':
#     test_anytime_gbfs = False
#     test_anytime_weighted_astar = True
#     if test_anytime_gbfs:
#         man_dist_solns = [4, 21, 18, 8, 18, -99, -99, 41, 15, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
#         len_benchmark = [4, 21, 18, 8, 18, 31, -99, 41, 15, -99, 73, 45, 57, 39, 37, 160, 137, -99, 259, -99]

#         ##############################################################
#         # TEST ANYTIME GBFS
#         print('Testing Anytime GBFS')
        
#         solved = 0; unsolved = []; benchmark = 0; timebound = 5 #5 second time limit 
#         arr = range(0, len(PROBLEMS))
#         for i in [19]:
#             print("*************************************")  
#             print("PROBLEM {}".format(i))

#             s0 = PROBLEMS[i] #Problems get harder as i gets bigger
#             final = anytime_gbfs(s0, heur_fn=heur_alternate, timebound=timebound)

#             if final:
#                 #final.print_path() #if you want to see the path
#                 if final.gval <= len_benchmark[i] or len_benchmark[i] == -99: #replace len_benchmark with man_dist_solns to compare with manhattan dist.
#                     benchmark += 1
#                 solved += 1 
#             else:
#                 unsolved.append(i)  

#         print("\n*************************************")  
#         print("Of {} initial problems, {} were solved in less than {} seconds by this solver.".format(len(PROBLEMS), solved, timebound))  
#         print("Of the {} problems that were solved, the cost of {} matched or outperformed the benchmark.".format(solved, benchmark))  
#         print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))  
#         print("The manhattan distance implementation solved 7 out of the 20 practice problems given 5 seconds.")
#         print("The better implementation solved 16 out of the 20 practice problems given 5 seconds.")
#         print("*************************************\n") 
#     if test_anytime_weighted_astar:

#         man_dist_solns = [4, 21, 10, 8, 17, -99, -99, 41, 14, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99, -99]
#         len_benchmark = [4, 21, 10, 8, 18, 31, -99, 41, 14, -99, 36, 30, 28, 31, 27, -99, -99, -99, -99, -99]

#         ##############################################################
#         # TEST ANYTIME WEIGHTED A STAR
#         print('Testing Anytime Weighted A Star')

#         solved = 0; unsolved = []; benchmark = 0; timebound = 5 #5 second time limit 
#         arr = range(0, len(PROBLEMS))
#         for i in [11]:
#             print("*************************************")  
#             print("PROBLEM {}".format(i))

#             s0 = PROBLEMS[i] #Problems get harder as i gets bigger
#             weight = 10 #note that if you want to over-ride this initial weight in your implementation, you are welcome to!
#             final = anytime_weighted_astar(s0, heur_fn=heur_alternate, weight=weight, timebound=timebound)

#             if final:   
#             #final.print_path()   
#                 if final.gval <= len_benchmark[i] or len_benchmark[i] == -99:
#                     benchmark += 1
#                 solved += 1 
#             else:
#                 unsolved.append(i)  

#         print("\n*************************************")  
#         print("Of {} initial problems, {} were solved in less than {} seconds by this solver.".format(len(PROBLEMS), solved, timebound))  
#         print("Of the {} problems that were solved, the cost of {} matched or outperformed the benchmark.".format(solved, benchmark))  
#         print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))  
#         print("The manhattan distance implementation solved 7 out of the 20 practice problems given 5 seconds.")
#         print("The better implementation solved 13 out of the 20 practice problems given 5 seconds.")
#         print("*************************************\n") 
#         ##############################################################

    # global countState
    # countState += 1
    # if countState >= 150000 and countState%1000==0:
    #     state.print_state()