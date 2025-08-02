import numpy as np
import os

def read_input_file(filename):
    """Read input from a text file"""
    with open(filename) as f:
        grid = []
        for line in f:
            row = [int(x.strip()) for x in line.strip().split(',')]
            grid.append(row)
        return np.array(grid)

def save_output_file(solution, filename):
    """Save solution to a text file"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        for row in solution:
            f.write("[ " + ", ".join(f'"{cell}"' for cell in row) + " ]\n")

def print_solution(solution, input_filename):
    """Print the solution in a readable format"""
    print(f"\nSolution for {input_filename}:")
    if solution is None:
        print("No solution found")
        return
    
    for row in solution:
        print("[", end="")
        print(", ".join(f'"{cell}"' for cell in row), end="")
        print("]")