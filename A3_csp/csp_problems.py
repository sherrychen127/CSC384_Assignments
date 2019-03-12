from csp import Constraint, Variable, CSP
from constraints import *
from backtracking import bt_search
import util


##################################################################
### NQUEENS
##################################################################

def nQueens(n, model):
    '''Return an n-queens CSP, optionally use tableContraints'''
    #your implementation for Question 4 changes this function
    #implement handling of model == 'alldiff'
    if not model in ['table', 'alldiff', 'row']:
        print("Error wrong sudoku model specified {}. Must be one of {}").format(
            model, ['table', 'alldiff', 'row'])
    i = 0
    dom = []
    for i in range(n):
        dom.append(i+1)
    vars = []
    for i in dom:
        vars.append(Variable('Q{}'.format(i), dom))
    cons = []
    if model == 'alldiff':
        #task 4
        var_name = ['Q{}'.format(i) for i in dom]
        cons.append(AllDiffConstraint("C({})".format(var_name), vars))
        for qi in range(len(dom)):
            for qj in range(qi+1, len(dom)):
                con = NeqConstraint("C(Q{},Q{})".format(qi+1,qj+1), [vars[qi], vars[qj]], qi+1, qj+1)
                cons.append(con) #binary not-equal constr
    else:
        constructor = QueensTableConstraint if model == 'table' else QueensConstraint
        for qi in range(len(dom)):
            for qj in range(qi+1, len(dom)):
                con = constructor("C(Q{},Q{})".format(qi+1,qj+1),
                                            vars[qi], vars[qj], qi+1, qj+1)
                cons.append(con)

    csp = CSP("{}-Queens".format(n), vars, cons)
    return csp

def solve_nQueens(n, algo, allsolns, model='row', variableHeuristic='fixed', trace=False):  ####change to False
    '''Create and solve an nQueens CSP problem. The first
       parameer is 'n' the number of queens in the problem,
       The second specifies the search algorithm to use (one
       of 'BT', 'FC', or 'GAC'), the third specifies if
       all solutions are to be found or just one, variableHeuristic
       specfies how the next variable is to be selected
       'random' at random, 'fixed' in a fixed order, 'mrv'
       minimum remaining values. Finally 'trace' if specified to be
       'True' will generate some output as the search progresses.
    '''
    csp = nQueens(n, model)
    solutions, num_nodes = bt_search(algo, csp, variableHeuristic, allsolns, trace)
    print("Explored {} nodes".format(num_nodes))
    if len(solutions) == 0:
        print("No solutions to {} found".format(csp.name()))
    else:
       print("Solutions to {}:".format(csp.name()))
       i = 0
       for s in solutions:
           i += 1
           print("Solution #{}: ".format(i)),
           for (var,val) in s:
               print("{} = {}, ".format(var.name(),val), end='')
           print("")


##################################################################
### Class Scheduling
##################################################################

NOCLASS='NOCLASS'
LEC='LEC'
TUT='TUT'
class ScheduleProblem:
    '''Class to hold an instance of the class scheduling problem.
       defined by the following data items
       a) A list of courses to take

       b) A list of classes with their course codes, buildings, time slots, class types, 
          and sections. It is specified as a string with the following pattern:
          <course_code>-<building>-<time_slot>-<class_type>-<section>

          An example of a class would be: CSC384-BA-10-LEC-01
          Note: Time slot starts from 1. Ensure you don't make off by one error!

       c) A list of buildings

       d) A positive integer N indicating number of time slots

       e) A list of pairs of buildings (b1, b2) such that b1 and b2 are close 
          enough for two consecutive classes.

       f) A positive integer K specifying the minimum rest frequency. That is, 
          if K = 4, then at least one out of every contiguous sequence of 4 
          time slots must be a NOCLASS.

        See class_scheduling.py for examples of the use of this class.
    '''

    def __init__(self, courses, classes, buildings, num_time_slots, connected_buildings, 
        min_rest_frequency):
        #do some data checks
        for class_info in classes:
            info = class_info.split('-')
            if info[0] not in courses:
                print("ScheduleProblem Error, classes list contains a non-course", info[0])
            if info[3] not in [LEC, TUT]:
                print("ScheduleProblem Error, classes list contains a non-lecture and non-tutorial", info[1])
            if int(info[2]) > num_time_slots or int(info[2]) <= 0:
                print("ScheduleProblem Error, classes list  contains an invalid class time", info[2])
            if info[1] not in buildings:
                print("ScheduleProblem Error, classes list  contains a non-building", info[3])

        for (b1, b2) in connected_buildings:
            if b1 not in buildings or b2 not in buildings:
                print("ScheduleProblem Error, connected_buildings contains pair with non-building (", b1, ",", b2, ")")

        if num_time_slots <= 0:
            print("ScheduleProblem Error, num_time_slots must be greater than 0")

        if min_rest_frequency <= 0:
            print("ScheduleProblem Error, min_rest_frequency must be greater than 0")

        #assign variables
        self.courses = courses
        self.classes = classes
        self.buildings = buildings
        self.num_time_slots = num_time_slots
        self._connected_buildings = dict()
        self.min_rest_frequency = min_rest_frequency

        #now convert connected_buildings to a dictionary that can be index by building.
        for b in buildings:
            self._connected_buildings.setdefault(b, [b])

        for (b1, b2) in connected_buildings:
            self._connected_buildings[b1].append(b2)
            self._connected_buildings[b2].append(b1)

    #some useful access functions
    def connected_buildings(self, building):
        '''Return list of buildings that are connected from specified building'''
        return self._connected_buildings[building]


def solve_schedules(schedule_problem, algo, allsolns,
                 variableHeuristic='mrv', silent=False, trace=False):
    #Your implementation for Question 6 goes here.
    #
    #Do not but do not change the functions signature
    #(the autograder will twig out if you do).

    #If the silent parameter is set to True
    #you must ensure that you do not execute any print statements
    #in this function.
    #(else the output of the autograder will become confusing).
    #So if you have any debugging print statements make sure you
    #only execute them "if not silent". (The autograder will call
    #this function with silent=True, class_scheduling.py will call
    #this function with silent=False)

    #You can optionally ignore the trace parameter
    #If you implemented tracing in your FC and GAC implementations
    #you can set this argument to True for debugging.
    #
    #Once you have implemented this function you should be able to
    #run class_scheduling.py to solve the test problems (or the autograder).
    #
    #
    '''This function takes a schedule_problem (an instance of ScheduleProblem
       class) as input. It constructs a CSP, solves the CSP with bt_search
       (using the options passed to it), and then from the set of CSP
       solution(s) it constructs a list (of lists) specifying possible schedule(s)
       for the student and returns that list (of lists)

       The required format of the list is:
       L[0], ..., L[N] is the sequence of class (or NOCLASS) assigned to the student.

       In the case of all solutions, we will have a list of lists, where the inner
       element (a possible schedule) follows the format above.
    '''

    #BUILD your CSP here and store it in the varable csp

    #build variable


    timeslot = initialize_timeslot(schedule_problem.num_time_slots) #declare a dict of time slot with same number of time slots
    classes_info = schedule_problem.classes
    required_courses = schedule_problem.courses #required courses
    lecture = []
    tutorial = []
    courses_lec = initialize_courses(required_courses) #initialize dictionary
    courses_tut = initialize_courses(required_courses)
    freq = schedule_problem.min_rest_frequency
    connected_buildings = schedule_problem._connected_buildings

    for class_info in classes_info:
        info = class_info.split('-')
        ts = int(info[2]) #char
        cur = timeslot[ts-1]
        cur.append(class_info) #construct domain
        timeslot[ts-1] = cur
        #print(timeslot[ts-1])
        if info[3] == LEC:
            lecture.append(class_info)
            if info[0] in required_courses:
                courses_lec[info[0]].append(class_info)  # all the classes for one course
        else: #tut
            tutorial.append(class_info)
            if info[0] in required_courses:
                courses_tut[info[0]].append(class_info)



    variables = []
    for i in timeslot.keys():
        variables.append(Variable('V{}'.format(i+1), timeslot[i])) #time slot start from 1 -> i+1
    c = []
    c1 = NValuesConstraint('all required lectures', variables, lecture, len(required_courses), len(required_courses))
    c2 = NValuesConstraint('all required tutorials', variables, tutorial, len(required_courses), len(required_courses))
    c.append(c1)
    c.append(c2)
    for lec in courses_lec.keys():
        c.append(NValuesConstraint('one lec per course', variables, courses_lec[lec], 1, 1))
    for tut in courses_tut.keys():
        c.append(NValuesConstraint('one tut per course', variables, courses_tut[tut], 1, 1))

    #no class in appropriate frequency
    if freq <= len(variables):
        for i in range(len(variables)-freq+1):
            c.append(NValuesConstraint('one NOCLASS per frequency', variables[i:i+freq], [NOCLASS], 1, freq))

    csp = CSP('schedule', variables, c)

    '''
    v1 = Variable('V1', [1, 2])
    v2 = Variable('V2', [1, 2])
    v3 = Variable('V3', [1, 2, 3, 4, 5])
    v4 = Variable('V4', [1, 2, 3, 4, 5])
    v5 = Variable('V5', [1, 2, 3, 4, 5])
    v6 = Variable('V6', [1, 2, 3, 4, 5, 6, 7, 8, 9])
    v7 = Variable('V7', [1, 2, 3, 4, 5, 6, 7, 8, 9])
    v8 = Variable('V8', [1, 2, 3, 4, 5, 6, 7, 8, 9])
    v9 = Variable('V9', [1, 2, 3, 4, 5, 6, 7, 8, 9])
    vars = [v1, v2, v3, v4, v5, v6, v7, v8, v9]
    nv9 = NValuesConstraint('9', vars, [9], 4, 5)
    nv1 = NValuesConstraint('1', vars, [1], 5, 5)
    testcsp = CSP('test', vars, [nv1, nv9])
    '''

    #invoke search with the passed parameters
    solutions, num_nodes = bt_search(algo, csp, variableHeuristic, allsolns, False)

    #Convert each solution into a list of lists specifying a schedule
    #for each student in the format described above.
    final_soln = []
    for soln in solutions:
        valid = True
        for course in required_courses:
            lec_index = -1
            tut_index = -1
            for i in range(len(soln)):
                #ts = chr(i+1) #turn into char
                (var, val) = soln[i]
                if val == NOCLASS:
                    continue
                info = val.split('-')
                #check tut and lecture time
                if info[0] == course and info[3] == LEC:
                    lec_index = int(info[2])
                elif info[0] == course and info[3] == TUT:
                    tut_index = int(info[2])
                if tut_index < lec_index and tut_index > 0 and lec_index > 0:
                    valid = False
                    break
            #check building
            for i in range(len(soln)-1):
                (var, val) = soln[i]
                (var2, val2) = soln[i+1]
                if val == NOCLASS or val2 == NOCLASS:
                    continue
                info = val.split('-')
                build = info[1]
                adj_info = val2.split('-')
                adj_build = adj_info[1]
                if adj_build not in connected_buildings[build]:
                    valid = False
                    break
            if not valid:
                break
        if valid:
            final_soln.append(soln)

    #convert to list format
    solns = []
    for soln in final_soln:
        solns.append([val for (var, val) in soln])

    #then return a list containing all converted solutions
    return solns

def initialize_courses(courses):
    dict = {}
    for course in courses:
        dict[course] = []
    return dict


def initialize_timeslot(numOfTs):
    dict = {}
    for i in range(numOfTs):
        dict[i] = [NOCLASS]
    return dict
