import time
import os
import matplotlib.pyplot as plt
import numpy as np
from hashi_board import HashiBoard
from optimizer import SolutionOptimizer
from pysat_solver import PySatSolver
from a_star_solver import AStarSolver
from brute_force_solver import BruteForceSolver
from backtracking_solver import BacktrackingSolver
from benchmark import Benchmark

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
        solution = solver.solve()
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
    methods = ['pysat', 'astar', 'backtracking', 'bruteforce']
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

def run_benchmark_analysis(input_dir='inputs'):
    """Run benchmark analysis and create visualizations"""
    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' not found!")
        return
    
    input_files = sorted([f for f in os.listdir(input_dir) if f.startswith('input-')])
    if not input_files:
        print(f"No input files found in '{input_dir}'!")
        return
    
    methods = ['pysat', 'astar', 'backtracking', 'bruteforce']
    results = {method: {'times': [], 'solved': [], 'files': []} for method in methods}
    
    print("Running benchmark analysis...")
    print("=" * 50)
    
    for input_file in input_files:
        input_path = os.path.join(input_dir, input_file)
        print(f"\nTesting {input_file}:")
        
        for method in methods:
            try:
                board = load_board(input_path)
                solution, elapsed = solve_with_method(board, method)
                
                solved = solution is not None and solution.is_valid_solution()
                results[method]['times'].append(elapsed)
                results[method]['solved'].append(solved)
                results[method]['files'].append(input_file)
                
                status = "✓ SOLVED" if solved else "✗ FAILED"
                print(f"  {method:12} - {elapsed:6.3f}s - {status}")
                
            except Exception as e:
                print(f"  {method:12} - ERROR: {str(e)}")
                results[method]['times'].append(float('inf'))
                results[method]['solved'].append(False)
                results[method]['files'].append(input_file)
    
    # Create visualizations
    create_benchmark_graphs(results, input_files)
    
    # Print summary
    print_benchmark_summary(results)

def create_benchmark_graphs(results, input_files):
    """Create and save benchmark visualization graphs"""
    
    # Set up the plotting style
    plt.style.use('default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Hashiwokakero Solver Benchmark Analysis', fontsize=16, fontweight='bold')
    
    methods = list(results.keys())
    colors = ['#2E86C1', '#28B463', '#F39C12', '#E74C3C']  # Blue, Green, Orange, Red
    
    # Graph 1: Average solving time comparison
    avg_times = []
    for method in methods:
        times = [t for t in results[method]['times'] if t != float('inf')]
        avg_times.append(np.mean(times) if times else 0)
    
    bars1 = ax1.bar(methods, avg_times, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_title('Average Solving Time by Method', fontweight='bold')
    ax1.set_ylabel('Time (seconds)')
    ax1.set_ylim(0, max(avg_times) * 1.1 if avg_times else 1)
    
    # Add value labels on bars
    for bar, time in zip(bars1, avg_times):
        if time > 0:
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_times)*0.01,
                    f'{time:.3f}s', ha='center', va='bottom', fontweight='bold')
    
    # Graph 2: Time comparison per test case
    x_pos = np.arange(len(input_files))
    width = 0.2
    
    for i, method in enumerate(methods):
        times = [t if t != float('inf') else 0 for t in results[method]['times']]
        ax2.bar(x_pos + i*width, times, width, label=method, color=colors[i], alpha=0.7)
    
    ax2.set_title('Solving Time per Test Case', fontweight='bold')
    ax2.set_xlabel('Test Cases')
    ax2.set_ylabel('Time (seconds)')
    ax2.set_xticks(x_pos + width * 1.5)
    ax2.set_xticklabels([f.replace('input-', '').replace('.txt', '') for f in input_files], rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the graph
    graph_filename = 'benchmark_analysis.png'
    plt.savefig(graph_filename, dpi=300, bbox_inches='tight')
    print(f"\nBenchmark graph saved as '{graph_filename}'")
    
    # Show the graph
    plt.show()

def print_benchmark_summary(results):
    """Print a detailed summary of benchmark results"""
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    
    methods = list(results.keys())
    
    for method in methods:
        times = [t for t in results[method]['times'] if t != float('inf')]
        solved_count = sum(results[method]['solved'])
        total_count = len(results[method]['solved'])
        
        print(f"\n{method.upper()}:")
        print(f"  Success Rate: {solved_count}/{total_count} ({solved_count/total_count*100:.1f}%)")
        if times:
            print(f"  Average Time: {np.mean(times):.3f}s")
            print(f"  Min Time:     {min(times):.3f}s")
            print(f"  Max Time:     {max(times):.3f}s")
        else:
            print(f"  No successful solutions")
    
    # Find best performer
    best_method = None
    best_score = float('-inf')
    
    for method in methods:
        solved_count = sum(results[method]['solved'])
        total_count = len(results[method]['solved'])
        success_rate = solved_count / total_count if total_count > 0 else 0
        
        times = [t for t in results[method]['times'] if t != float('inf')]
        avg_time = np.mean(times) if times else float('inf')
        
        # Score: prioritize success rate, then speed (lower time is better)
        score = success_rate * 100 - (avg_time if avg_time != float('inf') else 100)
        
        if score > best_score:
            best_score = score
            best_method = method
    
    print(f"\nBEST PERFORMER: {best_method.upper()}")
    print("="*60)

def show_menu():
    """Display the main menu and get user choice"""
    print("\n" + "="*50)
    print("HASHIWOKAKERO SOLVER")
    print("="*50)
    print("Choose an option:")
    print("1. Solve problems and generate outputs")
    print("2. Run benchmark analysis with graphs")
    print("3. Exit")
    print("-"*50)
    
    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return int(choice)
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            exit(0)

def main():
    """Main function with interactive menu"""
    while True:
        choice = show_menu()
        
        if choice == 1:
            print("\n🔧 Starting problem solving...")
            input_dir = input("Enter input directory (default: 'inputs'): ").strip() or 'inputs'
            output_dir = input("Enter output directory (default: 'outputs'): ").strip() or 'outputs'
            
            if os.path.exists(input_dir):
                process_all_inputs(input_dir, output_dir)
                print(f"\nProblem solving completed! Check '{output_dir}' for results.")
            else:
                print(f"❌ Input directory '{input_dir}' not found!")
            
        elif choice == 2:
            print("\nStarting benchmark analysis...")
            input_dir = input("Enter input directory (default: 'inputs'): ").strip() or 'inputs'
            run_benchmark_analysis(input_dir)
            
        elif choice == 3:
            print("\nThank you for using Hashiwokakero Solver!")
            break
        
        # Ask if user wants to continue
        if choice in [1, 2]:
            while True:
                continue_choice = input("\nDo you want to perform another operation? (y/n): ").strip().lower()
                if continue_choice in ['y', 'yes']:
                    break
                elif continue_choice in ['n', 'no']:
                    print("\nThank you for using Hashiwokakero Solver!")
                    return
                else:
                    print("Please enter 'y' for yes or 'n' for no.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("Please check your input files and try again.")