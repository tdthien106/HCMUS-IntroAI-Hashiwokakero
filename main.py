import time
import os
from hashi_board import HashiBoard
from optimizer import SolutionOptimizer
from pysat_solver import PySatSolver
from a_star_solver import AStarSolver
from brute_force_solver import BruteForceSolver
from backtracking_solver import BacktrackingSolver

def load_board(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    grid = []
    for line in lines:
        row = [int(x.strip()) for x in line.strip().split(',') if x.strip()]
        grid.append(row)
    return HashiBoard(grid)

def save_output(file_path, board):
    output_grid = board.to_output_grid()
    with open(file_path, 'w') as f:
        f.write('[\n')
        for row in output_grid:
            f.write('    ["' + '", "'.join(map(str, row)) + '"],\n')
        f.write(']\n')

def solve_with_method(board, method):
    start_time = time.time()
    
    if method == 'pysat':
        solver = PySatSolver(board)
        solved = solver.solve()
        solution = board if solved else None
    elif method == 'astar':
        solver = AStarSolver(board)
        solution = solver.solve()
    elif method == 'bruteforce':
        solver = BruteForceSolver(board)
        solution = solver.solve()
    elif method == 'backtracking':
        solver = BacktrackingSolver(board)
        solution = solver.solve()
    else:
        raise ValueError(f"Unknown method: {method}")
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    return solution, elapsed

def _solution_score(board):
    # Score based on bridge count and double bridges
    return sum(b['count'] for b in board.bridges) + \
           sum(1 for b in board.bridges if b['count'] == 2)

def find_optimal_solution(input_file):
    methods = ['pysat', 'astar', 'backtracking']
    best_solution = None
    
    for method in methods:
        board = load_board(input_file)
        solution, _ = solve_with_method(board, method)
        
        if solution and solution.is_valid_solution():
            # Optimize the solution
            optimizer = SolutionOptimizer(solution)
            optimized = optimizer.optimize()
            
            if not best_solution or _solution_score(optimized) < _solution_score(best_solution):
                best_solution = optimized
    
    return best_solution


def process_all_inputs(input_dir='inputs', output_dir='outputs'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    input_files = sorted([f for f in os.listdir(input_dir) if f.startswith('input-')])
    
    for input_file in input_files:
        input_path = os.path.join(input_dir, input_file)
        output_file = input_file.replace('input-', 'output-')
        output_path = os.path.join(output_dir, output_file)
        
        print(f"Processing {input_file}...")
        solution = find_optimal_solution(input_path)
        
        if solution:
            save_output(output_path, solution)
            print(f"Saved solution to {output_file}")
        else:
            print(f"No solution found for {input_file}")
        print("-" * 40)

if __name__ == '__main__':
    process_all_inputs()