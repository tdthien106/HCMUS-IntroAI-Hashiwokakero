import heapq
import time
from hashi_board import HashiBoard

class AStarSolver:
    def __init__(self, board):
        self.initial_board = board
        self.open_set = []
        self.closed_set = set()
        self.counter = 0  # Used as a tie-breaker
        
    def solve(self):
        # Initialize the open set with the starting board
        initial_state = self.initial_board
        heapq.heappush(self.open_set, (self._heuristic(initial_state), self.counter, initial_state))
        self.counter += 1
        
        while self.open_set:
            _, _, current = heapq.heappop(self.open_set)
            
            # Check if current state is solved
            if current.is_solved():
                return current
                
            # Generate next possible states
            for next_state in self._generate_successors(current):
                state_hash = self._board_hash(next_state)
                if state_hash not in self.closed_set:
                    f_score = self._heuristic(next_state)
                    heapq.heappush(self.open_set, (f_score, self.counter, next_state))
                    self.counter += 1
                    self.closed_set.add(state_hash)
                    
        return None  # No solution found
        
    def _heuristic(self, board):
            # Improved heuristic considering:
            # 1. Bridge deficit per island
            # 2. Connectivity
            # 3. Potential bridges that could be added
            
            total_deficit = 0
            connectivity_score = 0
            
            # Calculate bridge deficits
            island_info = {}
            for island in board.islands:
                pos = (island[0], island[1])
                island_info[pos] = {
                    'required': island[2],
                    'current': 0
                }

            for bridge in board.bridges:
                start = (bridge['start'][0], bridge['start'][1])
                end = (bridge['end'][0], bridge['end'][1])
                island_info[start]['current'] += bridge['count']
                island_info[end]['current'] += bridge['count']

            # Calculate deficit and potential bridges
            for pos, info in island_info.items():
                deficit = max(0, info['required'] - info['current'])
                total_deficit += deficit
                
                # Penalize islands with too many bridges
                if info['current'] > info['required']:
                    total_deficit += (info['current'] - info['required']) * 2

            # Calculate connectivity (number of separate components - 1)
            components = self._count_components(board)
            connectivity_score = components - 1 if components > 1 else 0

            return total_deficit * 10 + connectivity_score * 5
        
    def _count_components(self, board):
        if not board.islands:
            return 0
            
        visited = set()
        components = 0
        
        for island in board.islands:
            if island not in visited:
                components += 1
                stack = [island]
                
                while stack:
                    current = stack.pop()
                    if current in visited:
                        continue
                    visited.add(current)
                    
                    # Find connected islands
                    for bridge in board.bridges:
                        if (bridge['start'][0], bridge['start'][1]) == (current[0], current[1]):
                            end_island = next((i for i in board.islands if (i[0], i[1]) == (bridge['end'][0], bridge['end'][1])), None)
                            if end_island and end_island not in visited:
                                stack.append(end_island)
                        elif (bridge['end'][0], bridge['end'][1]) == (current[0], current[1]):
                            start_island = next((i for i in board.islands if (i[0], i[1]) == (bridge['start'][0], bridge['start'][1])), None)
                            if start_island and start_island not in visited:
                                stack.append(start_island)
                                
        return components
        
    def _generate_successors(self, board):
        successors = []
        
        # Try adding bridges between all possible island pairs
        for i, island1 in enumerate(board.islands):
            for island2 in board.islands[i+1:]:
                start = (island1[0], island1[1])
                end = (island2[0], island2[1])
                
                # Check if islands are aligned
                if start[0] == end[0] or start[1] == end[1]:
                    # Try adding single bridge
                    new_board = self._copy_board(board)
                    if new_board.add_bridge(start, end, 'h' if start[0] == end[0] else 'v'):
                        successors.append(new_board)
                        
                    # Try adding double bridge
                    new_board = self._copy_board(board)
                    if new_board.add_bridge(start, end, 'h' if start[0] == end[0] else 'v') and \
                       new_board.add_bridge(start, end, 'h' if start[0] == end[0] else 'v'):
                        successors.append(new_board)
                        
        return successors
        
    def _copy_board(self, board):
        new_board = HashiBoard([row[:] for row in board.grid])
        new_board.bridges = [bridge.copy() for bridge in board.bridges]
        return new_board
        
    def _board_hash(self, board):
        # Create a hashable representation of the board state
        bridges = []
        for bridge in sorted(board.bridges, key=lambda b: (b['start'], b['end'])):
            bridges.append((bridge['start'], bridge['end'], bridge['count']))
        return tuple(bridges)