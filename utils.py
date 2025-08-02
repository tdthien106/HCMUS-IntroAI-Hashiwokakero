import numpy as np
import os
import matplotlib.pyplot as plt
import json

def validate_grid(grid):
    """Validate the input grid"""
    if not isinstance(grid, (list, np.ndarray)):
        raise ValueError("Grid must be a 2D list or numpy array")
    
    if len(grid) == 0 or len(grid[0]) == 0:
        raise ValueError("Grid cannot be empty")
    
    for row in grid:
        for num in row:
            if not isinstance(num, (int, np.integer)):
                raise ValueError("All grid elements must be integers")
            if num < 0 or num > 8:
                raise ValueError("Island values must be between 0 and 8")

def plot_comparison(results):
    """Generate line chart comparing algorithm performance for each input"""
    os.makedirs("results", exist_ok=True)
    
    # Prepare data
    algorithms = ['SAT', 'Brute Force', 'Backtracking', 'A*']
    times = {algo: [] for algo in algorithms}
    puzzles = []
    
    # Collect data for each puzzle
    for puzzle, data in sorted(results.items()):
        if not isinstance(data, dict):
            continue
            
        puzzles.append(puzzle)
        for algo in algorithms:
            time_val = data.get(algo, float('inf'))
            times[algo].append(time_val if time_val != float('inf') else None)
    
    if not puzzles:
        print("No valid benchmark data to plot")
        return
    
    # Create line chart
    plt.figure(figsize=(12, 6))
    
    # Define colors and markers for each algorithm
    style = {
        'SAT': {'color': 'blue', 'marker': 'o', 'linestyle': '-'},
        'Brute Force': {'color': 'red', 'marker': 's', 'linestyle': '--'},
        'Backtracking': {'color': 'green', 'marker': '^', 'linestyle': '-.'},
        'A*': {'color': 'purple', 'marker': 'D', 'linestyle': ':'}
    }
    
    # Plot each algorithm's performance
    for algo in algorithms:
        valid_points = [(i, t) for i, t in enumerate(times[algo]) if t is not None]
        if not valid_points:
            continue
            
        x, y = zip(*valid_points)
        plt.plot(
            x, y, 
            label=algo, 
            color=style[algo]['color'], 
            marker=style[algo]['marker'], 
            linestyle=style[algo]['linestyle'],
            linewidth=2,
            markersize=8
        )
    
    # Customize chart
    plt.title('Algorithm Performance Comparison', fontsize=14, pad=20)
    plt.xlabel('Group 02 - Introduction AI', fontsize=12)
    plt.ylabel('Execution Time (seconds)', fontsize=12)
    plt.xticks(range(len(puzzles)), puzzles, rotation=45, ha='right')
    plt.yscale('log')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.legend(fontsize=10, framealpha=1)
    
    # Add value labels
    for algo in algorithms:
        for i, t in enumerate(times[algo]):
            if t is not None and t > 0:
                plt.text(
                    i, t, f'{t:.4f}', 
                    fontsize=8, 
                    color=style[algo]['color'],
                    ha='center', 
                    va='bottom' if algo == 'SAT' else 'top'
                )
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig("results/performance_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Performance comparison chart saved to results/performance_comparison.png")

def prepare_directories():
    """Ensure all required directories exist"""
    os.makedirs("inputs", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("benchmarks", exist_ok=True)
    os.makedirs("results", exist_ok=True)