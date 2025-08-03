import matplotlib.pyplot as plt
import matplotlib.patches as patches

def visualize_solution(puzzle, solution):
    """Visualize the puzzle and solution"""
    if not puzzle or not solution:
        print("No puzzle or solution to visualize")
        return
    
    height = len(puzzle)
    width = len(puzzle[0]) if height > 0 else 0
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Draw grid
    for i in range(height + 1):
        ax.axhline(i, color='black', lw=1)
    for j in range(width + 1):
        ax.axvline(j, color='black', lw=1)
    
    # Draw islands
    for i in range(height):
        for j in range(width):
            if puzzle[i][j] > 0:
                circle = patches.Circle((j + 0.5, i + 0.5), 0.3, 
                                       fill=True, color='blue')
                ax.add_patch(circle)
                ax.text(j + 0.5, i + 0.5, str(puzzle[i][j]), 
                       ha='center', va='center', color='white', fontsize=12)
    
    # Draw bridges
    for i in range(height):
        for j in range(width):
            if solution[i][j] > 0:
                # Horizontal bridges
                if j > 0 and solution[i][j-1] > 0:
                    if solution[i][j] == 1:
                        ax.plot([j - 0.5, j + 0.5], [i + 0.5, i + 0.5], 
                                'b-', lw=2)
                    elif solution[i][j] == 2:
                        ax.plot([j - 0.5, j + 0.5], [i + 0.4, i + 0.4], 
                                'b-', lw=2)
                        ax.plot([j - 0.5, j + 0.5], [i + 0.6, i + 0.6], 
                                'b-', lw=2)
                # Vertical bridges
                if i > 0 and solution[i-1][j] > 0:
                    if solution[i][j] == 1:
                        ax.plot([j + 0.5, j + 0.5], [i - 0.5, i + 0.5], 
                                'b-', lw=2)
                    elif solution[i][j] == 2:
                        ax.plot([j + 0.4, j + 0.4], [i - 0.5, i + 0.5], 
                                'b-', lw=2)
                        ax.plot([j + 0.6, j + 0.6], [i - 0.5, i + 0.5], 
                                'b-', lw=2)
    
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)  # Invert y-axis
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title("Hashiwokakero Solution")
    plt.show()