# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import random

import util
from game import Agent, Directions  # noqa
from util import manhattanDistance  # noqa
import math
import numpy as np
from enum import Enum


class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]


        curPos = currentGameState.getPacmanPosition()
        curFood = currentGameState.getFood()
        curFood = curFood.asList()

        if newPos == curPos:
            return float("-inf")
        for ghost in newGhostStates:
            if ghost.getPosition() == newPos:
                return float("-inf")
        food_dist = float("inf")

        for food in curFood:
            #if Directions.STOP in action:
            #    return float("-inf")
            food_dist = min(food_dist, mahattan_dist(food, newPos))
        return 1/(1 + food_dist)

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn="scoreEvaluationFunction", depth="2"):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"

        MaxNumOfAgents = gameState.getNumAgents()
        score, action = find_best(gameState, 0, MaxNumOfAgents, 0, self.depth, self.evaluationFunction)
        return action



def find_best(gameState, agentIndex, MaxNumOfAgents, d, max_depth, eval_function): #minCount from 1-n
    if gameState.isWin() or gameState.isLose() or d == max_depth: #if terminal node or non-terminal node at d = max depth
        return eval_function(gameState), -1
    else:
        legalAction = gameState.getLegalActions(agentIndex)
        if agentIndex == 0: #pacman
            for action in legalAction:
                if action == 'Stop' or action == Directions.STOP:
                    legalAction.remove(action)
            successor = [gameState.generateSuccessor(agentIndex, action) for action in legalAction]
            score = [find_best(state, agentIndex+1, MaxNumOfAgents, d, max_depth, eval_function)[0] for state in successor]
            best_action = legalAction[np.argmax(np.array(score))]
            return max(score), best_action
        else: #ghost
            successor = [gameState.generateSuccessor(agentIndex, action) for action in legalAction]
            if agentIndex == MaxNumOfAgents - 1:
                agentIndex = 0
                d += 1 #increment depth
            else:
                agentIndex += 1
            score = [find_best(state, agentIndex, MaxNumOfAgents, d, max_depth, eval_function)[0] for state in successor]
            best_action = legalAction[np.argmin(np.array(score))]

            return min(score), best_action


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        agentIndex = self.index
        MaxNumOfAgents = gameState.getNumAgents()
        #root = ABNode(gameState, agentIndex)
        #cur_depth = 0
        #curNode = root
        return AlphaBeta(gameState, agentIndex, MaxNumOfAgents, 0, self.depth, float("-inf"), float("inf"), self.evaluationFunction)
        #return AB_tree(root, curNode, agentIndex, MaxNumOfAgents, 0, self.depth, self.evaluationFunction)

'''
def AB_tree(root, curNode, agentIndex, MaxNumOfAgents, layer, max_depth, eval_function):
    curState = curNode.state
    legalAction = curState.getLegalActions(agentIndex)
    successor = [curState.generateSuccessor(agentIndex, action) for action in legalAction]
    if layer >= max_depth*MaxNumOfAgents or curState.isWin() or curState.isLose():
        curNode.score = eval_function(curState)
        return eval_function(curState)
    if agentIndex == 0: #pac man
        next_agent = agentIndex + 1
        action_score = []
        for i in range(len(successor)):
            successor_state = successor[i]
            curAction = legalAction[i]
            child = ABNode(successor_state, next_agent) #create new node
            curNode.add_child(child, curAction)
            curNode.score = max(curNode.score, AB_tree(root, child, next_agent, MaxNumOfAgents, layer+1, max_depth, eval_function))
            curNode.alpha = max(curNode.alpha, curNode.score) #update alpha
            curNode.pruned = curNode.alpha >= curNode.beta
            if layer == 0:
                action_score.append(curNode.score)
            if curNode.pruned:
                break
        if layer == 0:
            return legalAction[np.argmax(np.array(action_score))]
        return curNode.score
    else: #ghost
        next_agent = (agentIndex+1)%MaxNumOfAgents
        #depth += 1############
        for i in range(len(successor)):
            successor_state = successor[i]
            curAction = legalAction[i]
            child = ABNode(successor_state, next_agent)
            curNode.add_child(child, curAction)
            curNode.score = min(curNode.score, AB_tree(root, child, next_agent, MaxNumOfAgents, layer+1, max_depth, eval_function))
            curNode.beta = min(curNode.beta, curNode.score)
            curNode.pruned = curNode.alpha >= curNode.beta
            if curNode.pruned:
                break
        return curNode.score

#min = 0, max = 1
class ABNode:
    def __init__(self, gameState, agentIndex):
        if agentIndex == 0: #pacman max node
            self.score = float("-inf") #score of the current state
        else: #min Node
            self.score = float("inf")
        self.state = gameState
        self.action = None #action of the prev agent
        self.alpha = float("-inf") #initializa
        self.beta = float("inf") #initialize
        self.pruned = False #stop expanding current node
        self.agent = agentIndex #min node or max node
        self.children = [] #children

    def add_child(self, obj, prev_action):  #obj is the class of ABNode
        #children inherit the alpha and beta value of the parent

        obj.alpha = self.alpha
        obj.beta = self.beta
        obj.action = prev_action
        self.children.append(obj)
'''
def AlphaBeta(gameState, agentIndex, MaxNumOfAgents, layer, max_depth, alpha, beta, eval_function):
    if gameState.isWin() or gameState.isLose():
        return eval_function(gameState)
    if layer >= max_depth * MaxNumOfAgents: #reach to the desired depth
        return eval_function(gameState)

    #generate action array and successor states
    legalAction = [action for action in gameState.getLegalActions(agentIndex)]

    if agentIndex == 0: #pacman
        score = float("-inf")
        action_score = []
        for action in legalAction:
            successor = gameState.generateSuccessor(agentIndex, action)
            score = max(score, AlphaBeta(successor, agentIndex + 1, MaxNumOfAgents, layer+1, max_depth, alpha, beta, eval_function))
            alpha = max(alpha, score)
            if alpha >= beta: #alpha beta prune
                break
            if layer == 0:
                action_score.append(score) #if it is layer 1, return the action instead of the score
        if layer == 0:
            return legalAction[np.argmax(np.array(action_score))]
        return score
    else: #ghost
        nextAgent = (agentIndex + 1)%MaxNumOfAgents
        score = float("inf")
        for action in legalAction:
            successor = gameState.generateSuccessor(agentIndex, action)
            score = min(score, AlphaBeta(successor, nextAgent, MaxNumOfAgents, layer+1, max_depth, alpha, beta, eval_function))
            beta = min(beta, score) #update beta at min node
            if alpha >= beta: #alpha beta prune
                break
        return score


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        agentIndex = self.index
        MaxNumOfAgents = gameState.getNumAgents()
        return Expectimax(gameState, agentIndex, MaxNumOfAgents, 0, self.depth, self.evaluationFunction)


def Expectimax(gameState, agentIndex, MaxNumOfAgents, layer, max_depth, eval_function):
    if gameState.isWin() or gameState.isLose(): #reach terminal node
        return eval_function(gameState)
    if layer >= max_depth * MaxNumOfAgents: #reach to the desired depth
        return eval_function(gameState)

    legalAction = [action for action in gameState.getLegalActions(agentIndex)]
    if agentIndex == 0: #pacman

        score = float("-inf")
        action_score  = []
        for action in legalAction:
            successor = gameState.generateSuccessor(agentIndex, action)
            score = max(score, Expectimax(successor, agentIndex+1, MaxNumOfAgents, layer+1, max_depth, eval_function))
            if layer == 0:
                action_score.append(score)
        if layer == 0:
            return legalAction[np.argmax(np.array(action_score))]
        return score
    else:
        nextAgent = (agentIndex + 1)%(MaxNumOfAgents)
        score = 0
        #legalAction = [action for action in gameState.getLegalActions(agentIndex)]
        for action in legalAction:
            successor = gameState.generateSuccessor(agentIndex, action)
            score += Expectimax(successor, nextAgent, MaxNumOfAgents, layer+1, max_depth, eval_function)
        return score/len(legalAction)



def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"

    score = 0
    curPos = currentGameState.getPacmanPosition()
    curFood = currentGameState.getFood()
    curFood = curFood.asList()
    curGhostStates = currentGameState.getGhostStates()
    curScore = currentGameState.getScore()
    curPill = currentGameState.getCapsules()

    curScaredTimes = [ghostState.scaredTimer for ghostState in curGhostStates]
    food_dist = float("inf") #initialize distance to food
    pill_dist = float("inf") #initialize pill dist
    for pill in curPill:
        pill_dist = min(pill_dist, mahattan_dist(pill, curPos))
    for i in range(len(curScaredTimes)):
        ScaredTimes = curScaredTimes[i]
        curGhost = curGhostStates[i]
        ghost_dist = mahattan_dist(curGhost.getPosition(), curPos)
        if ScaredTimes > 0: #if ghost is scared
            if ghost_dist< 8:
                score += 2*(8 - ghost_dist) ** 2
            if pill_dist < 5:
                score += 1/(1+pill_dist)
        else:
            #score += ghost_dist * 4
            if ghost_dist<7:
                #score += ghost_dist**2
                score -= 2*(7 - ghost_dist) ** 2
        #score += math.sqrt(ScaredTimes)/2
    for food in curFood:
        food_dist = min(food_dist, mahattan_dist(food, curPos))
    score += 3/(1+food_dist)+ 2/(1+len(curFood))#1.5
    score += 0.4*curScore #0.4
    return score


def mahattan_dist(pos1, pos2):
    dist = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    return dist

def euclidian_dist(pos1, pos2):
    dist = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    return dist



# Abbreviation
better = betterEvaluationFunction



