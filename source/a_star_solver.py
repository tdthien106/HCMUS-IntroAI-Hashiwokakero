import heapq
import time
from collections import defaultdict
from hashi_board import HashiBoard

class AStarSolver:
    def __init__(self, board):
        self.initial_board = board
        self.open_set = []
        self.closed_set = set()
        self.counter = 0
        self.steps = 0
        
    def solve(self):
        # Create initial state
        initial_state = self._copy_board(self.initial_board)
        initial_score = self._heuristic(initial_state)
        heapq.heappush(self.open_set, (initial_score, self.counter, initial_state))
        self.counter += 1
        
        while self.open_set:
            self.steps += 1
            _, _, current = heapq.heappop(self.open_set)
            
            if current.is_solved():
                return current
                
            state_hash = self._board_hash(current)
            if state_hash in self.closed_set:
                continue
                
            self.closed_set.add(state_hash)
            
            for next_state in self._generate_successors(current):
                next_hash = self._board_hash(next_state)
                if next_hash not in self.closed_set:
                    f_score = self._heuristic(next_state)
                    heapq.heappush(self.open_set, (f_score, self.counter, next_state))
                    self.counter += 1
            
            # Early termination if taking too long
            if self.steps > 5000:
                break
                
        return None

    def _heuristic(self, board):
        total_score = 0
        island_info = {}
        
        # Initialize island requirements
        for island in board.islands:
            pos = (island[0], island[1])
            island_info[pos] = {
                'required': island[2],
                'current': 0
            }
        
        # Count current connections
        for bridge in board.bridges:
            start = (bridge['start'][0], bridge['start'][1])
            end = (bridge['end'][0], bridge['end'][1])
            island_info[start]['current'] += bridge['count']
            island_info[end]['current'] += bridge['count']
        
        # Calculate penalties
        connection_penalty = 0
        isolation_penalty = 0
        overconnection_penalty = 0
        
        for island in board.islands:
            pos = (island[0], island[1])
            info = island_info[pos]
            req = info['required']
            curr = info['current']
            
            if curr < req:
                connection_penalty += (req - curr) * 20
            elif curr > req:
                overconnection_penalty += (curr - req) * 40
            if curr == 0:
                isolation_penalty += 30
        
        # Connectivity analysis
        components = self._count_components(board)
        connectivity_penalty = (components - 1) * 60
        
        total_score = (
            connection_penalty + 
            overconnection_penalty + 
            isolation_penalty + 
            connectivity_penalty
        )
        
        return total_score

    def _count_components(self, board):
        if not board.islands:
            return 0
            
        visited = set()
        components = 0
        
        for island in board.islands:
            pos = (island[0], island[1])
            if pos not in visited:
                components += 1
                stack = [pos]
                
                while stack:
                    current = stack.pop()
                    if current in visited:
                        continue
                    visited.add(current)
                    
                    # Find connected islands
                    for bridge in board.bridges:
                        start = (bridge['start'][0], bridge['start'][1])
                        end = (bridge['end'][0], bridge['end'][1])
                        
                        if current == start and end not in visited:
                            stack.append(end)
                        elif current == end and start not in visited:
                            stack.append(start)
                            
        return components

    def _generate_successors(self, board):
        successors = []
        
        # Generate all possible bridge candidates
        for i, island1 in enumerate(board.islands):
            for island2 in board.islands[i+1:]:
                start = (island1[0], island1[1])
                end = (island2[0], island2[1])
                
                if board.is_valid_position_for_bridge(start, end):
                    # Try single bridge
                    new_board = self._copy_board(board)
                    if new_board.add_bridge(start, end, 'h' if start[0] == end[0] else 'v'):
                        successors.append(new_board)
                        
                    # Try double bridge
                    new_board = self._copy_board(board)
                    if (new_board.add_bridge(start, end, 'h' if start[0] == end[0] else 'v') and 
                       new_board.add_bridge(start, end, 'h' if start[0] == end[0] else 'v')):
                        successors.append(new_board)
                
        return successors

    def _board_hash(self, board):
        bridges = tuple(
            (bridge['start'][0], bridge['start'][1], 
             bridge['end'][0], bridge['end'][1], 
             bridge['count'])
            for bridge in sorted(board.bridges, key=lambda b: (b['start'], b['end']))
        )
        return bridges

    def _copy_board(self, board):
        """Create a deep copy of the board"""
        new_board = HashiBoard([row[:] for row in board.grid])
        new_board.bridges = [bridge.copy() for bridge in board.bridges]
        new_board.islands = board.islands.copy()
        return new_board