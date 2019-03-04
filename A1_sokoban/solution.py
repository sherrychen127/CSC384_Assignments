#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os #for time functions
from search import * #for search engines
from sokoban import SokobanState, Direction, PROBLEMS #for Sokoban specific classes and problems

def sokoban_goal_state(state):
  '''
  @return: Whether all boxes are stored.
  '''
  for box in state.boxes:
    if box not in state.storage:
      return False
  return True

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


    h = 0
    # occupied = []
    # print("new state")
    for box in state.boxes:
        nearest_storage = find_nearest_storage(state, box)
        h += calc_manhattan_dist(box, nearest_storage)
        # occupied.append(nearest_storage)

    return h



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

def heur_alternate(state):
#IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    #heur_manhattan_distance has flaws.
    #Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    #Your function should return a numeric value for the estimate of the distance to the goal.

    h_val = 0
    if is_deadlock(state):
        return float('inf')

    box_arr = []
    storage_arr = []
    for box in state.boxes:
        if box not in state.storage:
            box_arr.append(box)

    for storage_point in state.storage:
        if storage_point not in state.boxes:
            storage_arr.append(storage_point)

    w, h = len(box_arr), len(storage_arr)
    if w != h:
        return -1

    costMatrix = [[0 for x in range(w)] for y in range(h)]

    for i in range(w):
        for j in range(h):
            costMatrix[i][j] = calc_manhattan_dist(box_arr[i], storage_arr[j])

    # print("boxes, storage:", state.boxes, state.storage)
    marked = hungarianMethod(costMatrix)
    for i in range(len(marked)):
        box_index = marked[i][0]
        box = box_arr[box_index]
        storage_index = marked[i][1]

        nearest_storage_dist = calc_manhattan_dist(box, storage_arr[storage_index])
        h_val += nearest_storage_dist
        nearest_robot = find_nearest_robot(state, box)
        h_val += calc_manhattan_dist(box, nearest_robot)
        if is_edge(box, state) and nearest_storage_dist >= 2:
            h_val += 30  #20

        #robot.append(calc_manhattan_dist(box, find_nearest_robot(state, box)))
    '''
    for robot in state.robots:
        #robot_arr.append(calc_manhattan_dist(robot, find_nearest_box(state, robot)))
        nearest_box = find_nearest_box(state, robot)
        if nearest_box != None:
            h_val += calc_manhattan_dist(robot, find_nearest_box(state, robot))
    '''

    return h_val


def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def fval_function(sN, weight):
#IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

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
    return 0

def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
#IMPLEMENT
  '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
  '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of weighted astar algorithm'''
  return False

def anytime_gbfs(initial_state, heur_fn, timebound = 10):
    #IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of weighted astar algorithm'''


    se = SearchEngine('best_first', 'default')
    # se.trace_on(1)
    se.init_search(initial_state, sokoban_goal_state, heur_fn)
    # print("start")

    cur_soln = se.search(timebound)
    best_soln = cur_soln

    init_time = os.times()[0]
    cur_time = init_time

    # costbound = [g_values, h_values, f_values]
    costbound = [float("inf"), float("inf"), float("inf")]
    if cur_soln != False:
        costbound[0] = cur_soln.gval - 1
    # each time call a search, update the time bound with the remaining allowed time.
    while (cur_time < init_time + timebound):
        cur_soln = se.search(init_time + timebound - os.times()[0], costbound)
        if not cur_soln:
            return best_soln
        else:
            if cur_soln.gval < costbound[0]:
                best_soln = cur_soln
                costbound[0] = cur_soln.gval - 1
        cur_time = os.times()[0]
    return best_soln





##helper function###

#########
#@Return: int
#         manhattan dist between the box and its nearest storage
###################

def find_nearest_storage(state, box):
    minimum = 1000
    nearest_storage = None
    for storage_point in state.storage:
        manhattan_dist = calc_manhattan_dist(box, storage_point)
        if manhattan_dist<minimum:
            minimum = manhattan_dist
            #print("curren_min:",min)
            nearest_storage =  storage_point
    #print("box",box)
    #print("all storage", state.storage)
    #print("nearest_storage:", nearest_storage)

    return nearest_storage

def find_nearest_robot(state, box):
    minimum = 1000
    nearest_robot = None
    for robot in state.robots:
        manhattan_dist = calc_manhattan_dist(box, robot)
        if manhattan_dist < minimum:
            minimum = manhattan_dist
            nearest_robot = robot
    return nearest_robot

def find_nearest_box(state, robot):
    minimum = 1000
    nearest_box = None
    for box in state.boxes:
        manhattan_dist = calc_manhattan_dist(box, robot)
        if manhattan_dist < minimum and box not in state.storage:
            minimum = manhattan_dist
            nearest_box = box
    if minimum == 1000:
        return None
    return nearest_box


def calc_manhattan_dist(box, storage):
    if box == None or storage == None:
        return float('inf')
    return abs(box[0] - storage[0]) + abs(box[1] - storage[1])




##########
##### hungarian method ##########
#       Return tuples resulting from linear assignment
###########
def hungarianMethod(matrix):
    deleted_col = []
    deleted_row = []
    marked = []

    #step1: row reductioin and col reduction
    matrix = row_reduction(matrix)
    matrix = col_reduction(matrix)

    #step2: row scanning (&col scanning)
    #row scanning: if the row has exactly one zero, mark the zero and draw a vertical line

    matrix = cover_zero(matrix, deleted_row, deleted_col)
    marked = find_assignment(matrix, marked)

    #print("im here, print matrix", matrix)
    #print("im here", marked)

    return marked

def row_reduction(matrix):
    for row in matrix:
        min = find_min(row)
        if min is not None:
            for i in range(len(row)):
                row[i] = row[i] - min
    #print("done row redution")
    #print(matrix)
    return matrix

def col_reduction(matrix):

    for j in range(len(matrix)):
        min = 10000
        for i in range(len(matrix)):
            if matrix[i][j] < min:
                min = matrix[i][j]

        if min < 10000:
            for i in range(len(matrix)):
                matrix[i][j]-=min
    #print("done col reduction")
    #print(matrix)
    return matrix



def cover_zero(matrix, deleted_row, deleted_col):

    done = 0
    while not done:
        #initialize
        count = 0
        for i in range(len(matrix)):
            N = len(matrix) - i

            for row in range(len(matrix)):
                if row not in deleted_row and zero_count(matrix[row], deleted_col) == N:
                    count += 1
                    deleted_row.append(row)

            for col in range(len(matrix)):
                col_arr = []
                if col not in deleted_col:
                    for row in range(len(matrix)):

                        col_arr.append(matrix[row][col])
                if zero_count(col_arr, deleted_row) == N and col not in deleted_col:
                    count += 1
                    deleted_col.append(col)

        if count >= len(matrix):

            done = 1
        else:

            matrix = adjust_matrix(matrix, deleted_row, deleted_col)
            deleted_col = []
            deleted_row = []
    #print("covered zeros")
    return matrix



def find_assignment(matrix, marked):
    deleted_row = []
    deleted_col = []
    count = 0
    while True:
        count += 101
        if count > 100:
            return compromised(matrix,marked, deleted_col, deleted_row)
        for i in range(1, len(matrix)+1):
            for row in range(len(matrix)):
                if zero_count(matrix[row], []) == i:
                    for col in range(len(matrix)):
                        if matrix[row][col] == 0 and row not in deleted_row and col not in deleted_col:
                            deleted_col.append(col)
                            deleted_row.append(row)
                            tuple = (row, col)
                            marked.append(tuple)
                            break

            for col in range(len(matrix)):
                col_arr = []
                for row in range(len(matrix)):
                    col_arr.append(matrix[row][col])
                if zero_count(col_arr, deleted_row) == i:
                    for row in range(len(matrix)):
                        if matrix[row][col] == 0 and row not in deleted_row and col not in deleted_col :
                            deleted_row.append(row)
                            deleted_col.append(col)
                            tuple = (row,col)
                            marked.append(tuple)
        #print("marked len:",len(marked))
        #print("matrix len:", len(matrix))
        if len(marked) == len(matrix):
            break
        else:
            matrix = adjust_matrix(matrix, deleted_row,deleted_col )
            marked = []
            deleted_row = []
            deleted_col = []
    return marked


def adjust_matrix(matrix, deleted_row, deleted_col):
    remain_arr = []
    min = 100000
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if i not in deleted_row and j not in deleted_col:
                if matrix[i][j] < min:
                    min = matrix[i][j]
                tuple = (i,j)
                remain_arr.append(tuple)
    if min == 100000:
        return matrix
    for index in remain_arr:
        matrix[index[0]][index[1]] -= min
    #print("done adjusting matrix", matrix)
    return matrix


def compromised(matrix, marked, deleted_col, deleted_row):
    full = []
    for i in range(len(matrix)):
        full.append(i)
    for i in full:
        if i not in deleted_row:
            ind = -1
            min = 1000
            for j in range(len(matrix[i])):
                if j not in deleted_col and matrix[i][j] < min:
                    min = matrix[i][j]
                    ind = j

            marked.append((i,ind))
            deleted_row.append(i)
            deleted_col.append(ind)
    #print("compromised")
    return marked




def find_min(arr):
    #@INPUT: 1D array
    #@RETURN: minimum value
    if len(arr) == 0:
        return None
    min = arr[0]
    for entry in arr:
        if entry<min:
            min = entry
    return min


def zero_count(arr, deleted_arr):
    #@input(array, array)
    #@RETURN: integer (count of 0)
    count = 0
    for i in range(len(arr)):
        if i not in deleted_arr and arr[i] == 0:
            count += 1
    return count




###### detect deadlocks ######
def is_deadlock(state):
    w = state.width
    h = state.height
    #print("w,h", w,h)
    #print("boxes:",state.boxes)
    #print("storage:",state.storage)
    #print("obstacles:", state.obstacles)
    deadlock = []
    dir = [(1,0), (0,1), (-1,0), (0,-1)]  #right, down, left, up
    for i in range(w):
        deadlock.append((i,-1))
        deadlock.append((i,h))

    for j in range(h):
        deadlock.append((-1,j))
        deadlock.append((w,j))

    for obstacle in state.obstacles:
        deadlock.append(obstacle)
    for box in state.boxes:
        for i in range(len(dir)):
            if box + dir[i%(len(dir)-1)] in deadlock and box + dir[(i+1)%(len(dir)-1)] in deadlock and box not in state.storage:
                return True
    return False

def is_edge(box, state):
    w = state.width
    h = state.height
    if (box[0] == 0 or \
        box[1] == 0 or \
        box[0] == w - 1 or \
        box[1] == h - 1) and box not in state.storage:
        return True



