#STUDENT NAME: João Pedro Ferreira Monteiro
#STUDENT NUMBER: 114547

#DISCUSSED TPI-1 WITH: (names and numbers):


from tree_search import *
from strips import *
from blocksworld import *

class MyNode(SearchNode):

    def __init__(self,state,parent,cost,heuristic,action=None,arg6=None):
        super().__init__(state,parent)
        self.depth = 0 if parent is None else parent.depth + 1
        self.cost = cost
        self.heuristic = heuristic
        self.action = action

class MyTree(SearchTree):

    def __init__(self,problem, strategy='breadth',improve=False):
        super().__init__(problem,strategy)
        root = MyNode(problem.initial, None, 0, self.problem.domain.heuristic(problem.initial, problem.goal))
        self.open_nodes = [root]
        self.solution = None
        self.num_open = 1
        self.num_solution = 0
        self.num_skipped = 0
        self.num_closed = 0
        self.improve = improve

    def astar_add_to_open(self,lnewnodes):
        self.open_nodes.extend(lnewnodes)
        self.open_nodes.sort(key=lambda n: (n.cost + n.heuristic, n.depth, n.state))
        return self.open_nodes
    
    def informeddepth_add_to_open(self,lnewnodes):
        lnewnodes.sort(key=lambda n: (n.cost + n.heuristic, n.state))
        self.open_nodes = lnewnodes + self.open_nodes
        return self.open_nodes

    def search2(self):
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            self.num_open -= 1
            if self.improve and self.solution is not None:
                if (node.cost + node.heuristic) >= self.solution.cost:
                    if self.problem.goal_test(node.state):
                        self.num_solution += 1
                    else:
                        self.num_skipped += 1
                    continue 

            if self.problem.goal_test(node.state):
                if self.improve is False:
                    self.solution = node
                    self.num_solution += 1
                    return self.get_path(node)
                if self.solution is None:
                    self.solution = node
                    self.num_solution += 1
                elif node.cost < self.solution.cost:
                    self.solution = node
                    self.num_solution += 1
            else:
                self.num_closed += 1
                    
                lnewnodes = []
                for a in self.problem.domain.actions(node.state):
                    newstate = self.problem.domain.result(node.state,a)
                    
                    if newstate in self.get_path(node):
                        continue

                    cost = node.cost + self.problem.domain.cost(node.state, a)
                    heuristic = self.problem.domain.heuristic(newstate, self.problem.goal)
                    newnode = MyNode(newstate, node, cost, heuristic, a)
                    lnewnodes.append(newnode)

                self.add_to_open(lnewnodes)
                self.num_open = len(self.open_nodes)
        return self.get_path(self.solution)
 
    def check_admissible(self,node):
        sequence = self.get_sequence(node)
        for n in sequence:
            if n.heuristic > (node.cost - n.cost):
                return False
        return True

    def get_plan(self,node):
        if node.parent == None:
            return []
        plan = self.get_plan(node.parent)
        plan += [node.action]
        return plan

    # if needed, auxiliary methods can be added here
    
    def get_sequence(self,node):
        if node.parent == None:
            return [node]
        sequence = self.get_sequence(node.parent)
        sequence += [node]
        return sequence

class MyBlocksWorld(STRIPS):

    def heuristic(self, state, goal):
        def get_positions(current_state):
            positions = {}
            for s in current_state:
                if isinstance(s, Floor):
                    positions[s.args[0]] = ("Floor", None)
                elif isinstance(s, Holds):
                    positions[s.args[0]] = ("Holds", None)
                elif isinstance(s, On):
                    positions[s.args[0]] = ("On", s.args[1])
            return positions

        position_state = get_positions(state)
        position_goal = get_positions(goal)

        count = 0

        for item in position_state:
            if item not in position_goal:
                count += 1

        for block, goal_tup in position_goal.items():
            current_tup = position_state.get(block)
            if current_tup != goal_tup:
                count += 1
                if goal_tup[0] == "On":
                    base = goal_tup[1]
                    base_curr = position_state.get(base)
                    if base_curr != position_goal.get(base):
                        count += 1

        return count
