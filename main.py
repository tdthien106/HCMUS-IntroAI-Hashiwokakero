import os
import time
import matplotlib.pyplot as plt
from algorithms import (
    pysat_solver,
    astar_solver,
    backtracking_solver,
    brute_force_solver
)
from utils import (
    parse_puzzle,
    visualize,
    benchmark
)

# Define wrapper functions for each algorithm
def solve_pysat(puzzle):
    return pysat_solver(puzzle)

def solve_astar(puzzle):
    return astar_solver(puzzle)

def solve_backtracking(puzzle):
    return backtracking_solver(puzzle)

def solve_brute_force(puzzle):
    return brute_force_solver(puzzle)

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    """Print main menu"""
    clear_screen()
    print("Welcome to the Hashiwokakero Solver!")
    print("Choose an option:")
    print("0. Exit")
    print("Available algorithms:")  
    print("1. Solve with PySAT")
    print("2. Solve with A*")
    print("3. Solve with Backtracking")
    print("4. Solve with Brute Force")
    print("5. Benchmark all algorithms")
    print("0. Exit")
    print("\n")

def get_input_files():
    """Get all input files from inputs directory"""
    if not os.path.exists("inputs"):
        os.makedirs("inputs")
        print("Created inputs directory. Please add your input files there.")
        return []
    
    input_files = [f for f in os.listdir("inputs") if f.startswith("input-") and f.endswith(".txt")]
    if not input_files:
        print("No input files found in inputs directory. Files should be named input-*.txt")
    return sorted(input_files)

def solve_with_algorithm(algorithm, algorithm_name):
    """Solve all input files with specified algorithm"""
    input_files = get_input_files()
    if not input_files:
        return
    
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
    
    total_time = 0
    solved_count = 0
    
    for input_file in input_files:
        try:
            print(f"\nProcessing {input_file} with {algorithm_name}...")
            puzzle = parse_puzzle(f"inputs/{input_file}")
            
            start_time = time.time()
            solution = algorithm(puzzle)
            elapsed_time = time.time() - start_time
            total_time += elapsed_time
            
            if solution:
                solved_count += 1
                output_file = f"output-{input_file.replace('input-', '')}"
                output_path = f"outputs/{output_file}"
                
                with open(output_path, 'w') as f:
                    for row in solution:
                        f.write(" ".join(map(str, row)) + "\n")
                
                print(f"Solution found in {elapsed_time:.4f} seconds")
                print(f"Solution saved to {output_path}")
                visualize(puzzle, solution)
            else:
                print(f"No solution found for {input_file}")
                
        except Exception as e:
            print(f"Error processing {input_file}: {str(e)}")
    
    print(f"\nSummary for {algorithm_name}:")
    print(f"- Total puzzles: {len(input_files)}")
    print(f"- Solved: {solved_count}")
    print(f"- Success rate: {(solved_count/len(input_files))*100:.2f}%")
    print(f"- Total time: {total_time:.4f} seconds")
    print(f"- Average time per puzzle: {total_time/len(input_files):.4f} seconds")

def run_benchmark_mode():
    """Run benchmark on all input files"""
    input_files = get_input_files()
    if not input_files:
        return
    
    if not os.path.exists("outputs/benchmarks"):
        os.makedirs("outputs/benchmarks")
    
    algorithms = {
        "PySAT": solve_pysat,
        "A*": solve_astar,
        "Backtracking": solve_backtracking,
        "Brute Force": solve_brute_force
    }
    
    benchmark_results = {}
    
    for input_file in input_files:
        print(f"\nBenchmarking {input_file}...")
        puzzle = parse_puzzle(f"inputs/{input_file}")
        
        results = {}
        for name, algorithm in algorithms.items():
            try:
                print(f"  Running {name}...", end=" ", flush=True)
                start_time = time.time()
                solution = algorithm(puzzle)
                elapsed_time = time.time() - start_time
                
                results[name] = {
                    "time": elapsed_time,
                    "solved": solution is not None
                }
                
                print(f"Done in {elapsed_time:.4f} seconds - {'Solved' if solution else 'No solution'}")
            except Exception as e:
                print(f"Error running {name}: {str(e)}")
                results[name] = {
                    "time": -1,
                    "solved": False
                }
        
        benchmark_results[input_file] = results
        
        # Plot results for this input file
        plot_benchmark_results(input_file, results)
    
    print("\nBenchmark completed!")
    print_summary_table(benchmark_results)

def plot_benchmark_results(input_file, results):
    """Plot benchmark results for a single input file"""
    names = [name for name in results if results[name]["time"] >= 0]
    times = [results[name]["time"] for name in names]
    solved = ["Solved" if results[name]["solved"] else "Failed" for name in names]
    
    colors = ['green' if s == "Solved" else 'red' for s in solved]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, times, color=colors)
    plt.ylabel("Time (seconds)")
    plt.title(f"Algorithm Performance - {input_file}")
    
    # Add time labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}s',
                ha='center', va='bottom')
    
    # Create legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', label='Solved'),
        Patch(facecolor='red', label='Failed')
    ]
    plt.legend(handles=legend_elements)
    
    # Save plot
    plot_filename = f"benchmark-{input_file.replace('.txt', '')}.png"
    plot_path = f"outputs/benchmarks/{plot_filename}"
    plt.savefig(plot_path)
    plt.close()
    
    print(f"Benchmark plot saved to {plot_path}")

def print_summary_table(results):
    """Print summary table of benchmark results"""
    print("\nSUMMARY TABLE:")
    print("+" + "-"*50 + "+")
    print("| {:<20} | {:<8} | {:<8} | {:<8} |".format(
        "Algorithm", "Solved", "Failed", "Avg Time"))
    print("+" + "-"*50 + "+")
    
    # Get all algorithm names from first result
    algorithms = list(next(iter(results.values())).keys())
    
    for algo in algorithms:
        solved = 0
        failed = 0
        total_time = 0
        valid_runs = 0
        
        for input_file in results:
            if results[input_file][algo]["time"] >= 0:
                valid_runs += 1
                if results[input_file][algo]["solved"]:
                    solved += 1
                else:
                    failed += 1
                total_time += results[input_file][algo]["time"]
        
        avg_time = total_time / valid_runs if valid_runs > 0 else 0
        print("| {:<20} | {:<8} | {:<8} | {:<8.4f} |".format(
            algo, solved, failed, avg_time))
    
    print("+" + "-"*50 + "+")

def main():
    while True:
        clear_screen()
        print_menu()
        
        try:
            choice = int(input("Enter your choice (0-5): "))
        except ValueError:
            input("Invalid input. Press Enter to continue...")
            continue
        
        if choice == 0:
            print("Exiting program...")
            break
        elif choice == 1:
            solve_with_algorithm(solve_pysat, "PySAT")
        elif choice == 2:
            solve_with_algorithm(solve_astar, "A*")
        elif choice == 3:
            solve_with_algorithm(solve_backtracking, "Backtracking")
        elif choice == 4:
            solve_with_algorithm(solve_brute_force, "Brute Force")
        elif choice == 5:
            run_benchmark_mode()
        else:
            input("Invalid choice. Press Enter to continue...")
            continue
        
        input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    main()