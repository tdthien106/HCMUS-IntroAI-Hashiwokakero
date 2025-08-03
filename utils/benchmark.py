import time
import matplotlib.pyplot as plt
from algorithms import (
    pysat_solver,
    astar_solver,
    backtracking_solver,
    brute_force_solver
)
import os

def run_benchmark(puzzle, input_filename):
    algorithms = {
        "PySAT": pysat_solver.solve,
        "A*": astar_solver.solve,
        "Brute Force": brute_force.solve,
        "Backtracking": backtracking.solve
    }
    
    results = {}
    
    for name, solver in algorithms.items():
        print(f"\nRunning {name} algorithm...")
        start_time = time.time()
        
        try:
            solution = solver(puzzle)
            elapsed_time = time.time() - start_time
            
            results[name] = {
                "time": elapsed_time,
                "solution": solution is not None
            }
            
            print(f"Completed in {elapsed_time:.4f} seconds")
            print(f"Solution found: {'Yes' if solution else 'No'}")
            
            # Save solution
            if solution:
                output_filename = f"output-{os.path.splitext(input_filename)[0]}-{name.lower().replace(' ', '_')}.txt"
                output_path = f"outputs/{output_filename}"
                
                with open(output_path, 'w') as f:
                    for row in solution:
                        f.write(" ".join(map(str, row)) + "\n")
                
                print(f"Solution saved to {output_path}")
        except Exception as e:
            print(f"Error running {name}: {str(e)}")
            results[name] = {
                "time": -1,
                "solution": False
            }
    
    # Plot results
    plot_results(results, input_filename)
    
    return results

def plot_results(results, input_filename):
    names = [name for name in results if results[name]["time"] >= 0]
    times = [results[name]["time"] for name in names]
    solved = ["Solved" if results[name]["solution"] else "Failed" for name in names]
    
    colors = ['green' if s == "Solved" else 'red' for s in solved]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, times, color=colors)
    plt.ylabel("Time (seconds)")
    plt.title(f"Algorithm Performance Comparison for {input_filename}")
    
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
    os.makedirs("outputs/benchmarks", exist_ok=True)
    plot_filename = f"benchmark-{os.path.splitext(input_filename)[0]}.png"
    plot_path = f"outputs/benchmarks/{plot_filename}"
    plt.savefig(plot_path)
    plt.close()
    
    print(f"\nBenchmark results saved to {plot_path}")