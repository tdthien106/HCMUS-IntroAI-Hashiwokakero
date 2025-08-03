from itertools import product
from hashi_board import HashiBoard

class BruteForceSolver:
    def __init__(self, board):
        self.board = board
        
    def solve(self):
        # Generate all possible bridges between islands
        potential_bridges = self._generate_potential_bridges()
        
        # Try all possible combinations of bridges
        for bridge_counts in product([0, 1, 2], repeat=len(potential_bridges)):
            test_board = self._copy_board(self.board)
            valid = True
            
            for i, count in enumerate(bridge_counts):
                if count > 0:
                    bridge = potential_bridges[i]
                    start = (bridge[0][0], bridge[0][1])
                    end = (bridge[1][0], bridge[1][1])
                    bridge_type = 'h' if start[0] == end[0] else 'v'
                    
                    for _ in range(count):
                        if not test_board.add_bridge(start, end, bridge_type):
                            valid = False
                            break
                    if not valid:
                        break
                        
            if valid and test_board.is_solved():
                return test_board
                
        return None
        
    def _generate_potential_bridges(self):
        bridges = []
        for i, island1 in enumerate(self.board.islands):
            for island2 in self.board.islands[i+1:]:
                # Check if islands are aligned horizontally or vertically
                if island1[0] == island2[0] or island1[1] == island2[1]:
                    bridges.append((island1, island2))
        return bridges
        
    def _copy_board(self, board):
        new_board = HashiBoard([row[:] for row in board.grid])
        new_board.bridges = [bridge.copy() for bridge in board.bridges]
        return new_board