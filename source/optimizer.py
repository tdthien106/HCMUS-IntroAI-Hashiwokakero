from hashi_board import HashiBoard

class SolutionOptimizer:
    def __init__(self, board):
        self.original_board = board
        self.best_board = None
        self.best_score = float('inf')

    def optimize(self):
        self._try_optimize(self.original_board)
        return self.best_board if self.best_board else self.original_board

    def _try_optimize(self, board):
        current_score = self._score_solution(board)
        if current_score < self.best_score:
            self.best_board = self._copy_board(board)
            self.best_score = current_score

        # Try removing redundant bridges
        for i in range(len(board.bridges)):
            new_board = self._copy_board(board)
            del new_board.bridges[i]
            if new_board.is_valid_solution():
                self._try_optimize(new_board)

        # Try reducing double bridges to single
        for i in range(len(board.bridges)):
            if board.bridges[i]['count'] == 2:
                new_board = self._copy_board(board)
                new_board.bridges[i]['count'] = 1
                if new_board.is_valid_solution():
                    self._try_optimize(new_board)

    def _score_solution(self, board):
        # Score based on:
        # 1. Number of bridges (fewer is better)
        # 2. Number of double bridges (fewer is better)
        total_bridges = sum(b['count'] for b in board.bridges)
        double_bridges = sum(1 for b in board.bridges if b['count'] == 2)
        return total_bridges * 2 + double_bridges * 3

    def _copy_board(self, board):
        new_board = HashiBoard([row[:] for row in board.grid])
        new_board.bridges = [bridge.copy() for bridge in board.bridges]
        return new_board