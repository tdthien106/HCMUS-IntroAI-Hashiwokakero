import heapq
from copy import deepcopy

class State:
    def __init__(self, puzzle, bridges=None):
        self.puzzle = puzzle
        self.height = len(puzzle)
        self.width = len(puzzle[0]) if self.height > 0 else 0
        self.bridges = bridges if bridges else []
        self.remaining = self.calculate_remaining()
        
    def calculate_remaining(self):
        remaining = {}
        # Initialize with required bridges
        for i in range(self.height):
            for j in range(self.width):
                if self.puzzle[i][j] > 0:
                    remaining[(i, j)] = self.puzzle[i][j]
        
        # Subtract existing bridges
        for (i1, j1, i2, j2), count in self.bridges:
            remaining[(i1, j1)] -= count
            remaining[(i2, j2)] -= count
        
        return remaining
    
    def is_goal(self):
        return all(v == 0 for v in self.remaining.values())
    
    def get_key(self):
        return tuple(sorted(self.bridges))
    
    def heuristic(self):
        return sum(abs(v) for v in self.remaining.values())
    
    def get_neighbors(self):
        neighbors = []
        
        # Find all possible bridges we could add
        for i1 in range(self.height):
            for j1 in range(self.width):
                if self.puzzle[i1][j1] > 0 and self.remaining.get((i1, j1), 0) > 0:
                    # Look for connectable islands
                    # Horizontal right
                    for j2 in range(j1 + 1, self.width):
                        if self.puzzle[i1][j2] > 0:
                            if self.can_add_bridge(i1, j1, i1, j2):
                                for count in [1, 2]:
                                    if self.can_add_bridge(i1, j1, i1, j2, count):
                                        new_bridges = deepcopy(self.bridges)
                                        new_bridges.append(((i1, j1, i1, j2), count))
                                        neighbors.append(State(self.puzzle, new_bridges))
                            break
                    # Vertical down
                    for i2 in range(i1 + 1, self.height):
                        if self.puzzle[i2][j1] > 0:
                            if self.can_add_bridge(i1, j1, i2, j1):
                                for count in [1, 2]:
                                    if self.can_add_bridge(i1, j1, i2, j1, count):
                                        new_bridges = deepcopy(self.bridges)
                                        new_bridges.append(((i1, j1, i2, j1), count))
                                        neighbors.append(State(self.puzzle, new_bridges))
                            break
        return neighbors
    
    def can_add_bridge(self, i1, j1, i2, j2, count=1):
        # Check if bridge would exceed island capacity
        if (self.remaining.get((i1, j1), 0) < count or 
            self.remaining.get((i2, j2), 0) < count):
            return False
        
        # Check if bridge already exists
        for (bi1, bj1, bi2, bj2), bcount in self.bridges:
            if ((bi1 == i1 and bj1 == j1 and bi2 == i2 and bj2 == j2) or 
                (bi1 == i2 and bj1 == j2 and bi2 == i1 and bj2 == j1)):
                if bcount + count > 2:
                    return False
        
        # Check if bridge would cross any existing bridges
        if i1 == i2:  # Horizontal bridge
            for (xi1, xj1, xi2, xj2), _ in self.bridges:
                if xi1 != xi2:  # Vertical bridge
                    if (xj1 > min(j1, j2) and xj1 < max(j1, j2) and 
                        xi1 < i1 and xi2 > i1):
                        return False
        else:  # Vertical bridge
            for (xi1, xj1, xi2, xj2), _ in self.bridges:
                if xj1 == xj2:  # Horizontal bridge
                    if (xi1 > min(i1, i2) and xi1 < max(i1, i2) and 
                        xj1 < j1 and xj2 > j1):
                        return False
        
        return True

def solve(puzzle):
    """Solve Hashiwokakero puzzle using A* search"""
    initial_state = State(puzzle)
    
    open_set = []
    heapq.heappush(open_set, (initial_state.heuristic(), initial_state))
    
    closed_set = set()
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current.is_goal():
            return convert_to_solution(current)
            
        if current.get_key() in closed_set:
            continue
            
        closed_set.add(current.get_key())
        
        for neighbor in current.get_neighbors():
            heapq.heappush(open_set, (neighbor.heuristic(), neighbor))
    
    return None

def convert_to_solution(state):
    """Convert state to solution matrix"""
    solution = [[0 for _ in range(state.width)] for _ in range(state.height)]
    
    for (i1, j1, i2, j2), count in state.bridges:
        if i1 == i2:  # Horizontal bridge
            for j in range(min(j1, j2), max(j1, j2) + 1):
                solution[i1][j] = max(solution[i1][j], count)
        else:  # Vertical bridge
            for i in range(min(i1, i2), max(i1, i2) + 1):
                solution[i][j1] = max(solution[i][j1], count)
    
    return solution