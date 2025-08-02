from parsers import read_input_file, save_output_file, print_solution
from solver import HashiwokakeroSolver
from utils import validate_grid, plot_comparison, prepare_directories
import os
import glob
import json
import time

def process_puzzle(input_file, output_file):
    """Process a single puzzle file"""
    try:
        grid = read_input_file(input_file)
        validate_grid(grid)
        
        solver = HashiwokakeroSolver(grid)
        
        # Solve with SAT (primary solution)
        solution, _ = solver.solve()
        
        # Save and print solution
        print_solution(solution, input_file)
        if solution is not None:
            save_output_file(solution, output_file)
        
        return solution is not None
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")
        return False

def benchmark_algorithms():
    """Run benchmarks comparing all algorithms"""
    prepare_directories()
    input_files = sorted(glob.glob("inputs/input-*.txt"))
    results = {}
    
    print("\nRunning benchmarks...")
    print("="*50)
    
    for input_file in input_files:
        puzzle_name = os.path.basename(input_file)
        try:
            grid = read_input_file(input_file)
            validate_grid(grid)
            
            solver = HashiwokakeroSolver(grid)
            comparison = solver.compare_algorithms()
            results[puzzle_name] = comparison
            
            # Print individual results
            print(f"\nResults for {puzzle_name}:")
            for algo, time_taken in comparison.items():
                status = f"{time_taken:.6f}s" if time_taken != float('inf') else "Failed"
                print(f"{algo:<12}: {status}")
        
        except Exception as e:
            print(f"\nError benchmarking {puzzle_name}: {str(e)}")
            results[puzzle_name] = None
    
    # Save and plot results
    os.makedirs("benchmarks", exist_ok=True)
    with open("benchmarks/results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    plot_comparison(results)
    print("\nBenchmark results saved to:")
    print("- benchmarks/results.json")
    print("- results/performance_comparison.png")

def main():
    prepare_directories()
    
    print("Hashiwokakero Puzzle Solver")
    print("1. Solve puzzles")
    print("2. Benchmark algorithms")
    choice = input("Select option (1/2): ")
    
    if choice == '1':
        input_files = glob.glob("inputs/input-*.txt")
        if not input_files:
            print("No input files found in inputs/ directory")
            print("Please create input files named input-1.txt, input-2.txt, etc.")
            return
        
        success_count = 0
        for input_file in input_files:
            output_file = os.path.join("outputs", os.path.basename(input_file).replace("input-", "output-"))
            if process_puzzle(input_file, output_file):
                success_count += 1
        
        print(f"\nProcessed {len(input_files)} files, {success_count} successfully solved")
    
    elif choice == '2':
        benchmark_algorithms()
    
    else:
        print("Invalid option selected")

if __name__ == "__main__":
    main()