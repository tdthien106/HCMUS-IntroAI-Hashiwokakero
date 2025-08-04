from hashi_board import HashiBoard

class BacktrackingSolver:
    def __init__(self, board):
        self.board = board
        self.solution = None
        
    def solve(self):
        self._backtrack(self.board)
        return self.solution
        
    def _backtrack(self, current_board):
        if current_board.is_solved():
            self.solution = current_board
            return True
            
        # Find the next island to connect
        for island in current_board.islands:
            current_value = current_board.get_island_value(island[0], island[1])
            connected = 0
            for bridge in current_board.bridges:
                if (bridge['start'][0] == island[0] and bridge['start'][1] == island[1]) or \
                   (bridge['end'][0] == island[0] and bridge['end'][1] == island[1]):
                    connected += bridge['count']
                    
            if connected < current_value:
                # Try connecting to other islands
                for other in current_board.islands:
                    if other != island:
                        start = (island[0], island[1])
                        end = (other[0], other[1])
                        
                        # Try adding single bridge
                        new_board = self._copy_board(current_board)
                        if new_board.add_bridge(start, end, 'h' if start[0] == end[0] else 'v'):
                            if self._backtrack(new_board):
                                return True
                                
                        # Try adding double bridge
                        new_board = self._copy_board(current_board)
                        if new_board.add_bridge(start, end, 'h' if start[0] == end[0] else 'v') and \
                           new_board.add_bridge(start, end, 'h' if start[0] == end[0] else 'v'):
                            if self._backtrack(new_board):
                                return True
                                
                break  # Only try one incomplete island at a time
                
        return False
        
    def _copy_board(self, board):
        new_board = HashiBoard([row[:] for row in board.grid])
        new_board.bridges = [bridge.copy() for bridge in board.bridges]
        return new_board