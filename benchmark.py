import time
import pandas as pd
from tabulate import tabulate

class Benchmark:
    def __init__(self):
        self.results = []
    
    def run(self, board, methods):
        for method in methods:
            start_time = time.time()
            result = self._run_method(board, method)
            end_time = time.time()
            
            self.results.append({
                'Method': method,
                'Time (s)': round(end_time - start_time, 4),
                'Solved': result['solved'],
                'Bridges': result['bridges'],
                'Steps': result['steps'],
                'Valid': result['valid']
            })
    
    def _run_method(self, board, method):
        from pysat_solver import PySatSolver
        from a_star_solver import AStarSolver
        from brute_force_solver import BruteForceSolver
        from backtracking_solver import BacktrackingSolver
        
        board_copy = board.copy()
        steps = 0
        
        if method == 'pysat':
            solver = PySatSolver(board_copy)
            solved = solver.solve()
            steps = len(solver.clauses)
        elif method == 'astar':
            solver = AStarSolver(board_copy)
            solution = solver.solve()
            solved = solution is not None
            steps = solver.steps
        elif method == 'bruteforce':
            solver = BruteForceSolver(board_copy)
            solution = solver.solve()
            solved = solution is not None
            steps = solver.combinations_tried
        elif method == 'backtracking':
            solver = BacktrackingSolver(board_copy)
            solution = solver.solve()
            solved = solution is not None
            steps = solver.backtrack_steps
        
        return {
            'solved': solved,
            'bridges': len(board_copy.bridges) if solved else 0,
            'steps': steps,
            'valid': board_copy.is_valid_solution() if solved else False
        }
    
    def show_results(self):
        df = pd.DataFrame(self.results)
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    
    def save_to_csv(self, filename):
        pd.DataFrame(self.results).to_csv(filename, index=False)