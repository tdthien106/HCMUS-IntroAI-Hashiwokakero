from itertools import product

def solve(puzzle):
    """Brute force solution for small puzzles"""
    height = len(puzzle)
    width = len(puzzle[0]) if height > 0 else 0
    
    # Find all islands
    islands = []
    for i in range(height):
        for j in range(width):
            if puzzle[i][j] > 0:
                islands.append((i, j, puzzle[i][j]))
    
    # Generate all possible connections
    connections = []
    for idx1, (i1, j1, _) in enumerate(islands):
        for idx2, (i2, j2, _) in enumerate(islands[idx1+1:], idx1+1):
            if i1 == i2 or j1 == j2:  # Same row or column
                connections.append((i1, j1, i2, j2))
    
    # Try all possible combinations (very inefficient)
    for bridge_counts in product([0, 1, 2], repeat=len(connections)):
        solution = [[0 for _ in range(width)] for _ in range(height)]
        valid = True
        
        # Apply bridges
        for (i1, j1, i2, j2), count in zip(connections, bridge_counts):
            if count > 0:
                if i1 == i2:  # Horizontal
                    for j in range(min(j1, j2), max(j1, j2) + 1):
                        solution[i1][j] += count
                else:  # Vertical
                    for i in range(min(i1, i2), max(i1, i2) + 1):
                        solution[i][j1] += count
        
        # Check if solution is valid
        for i in range(height):
            for j in range(width):
                if puzzle[i][j] > 0:
                    total = 0
                    # Count horizontal bridges
                    if j > 0 and solution[i][j-1] > 0 and solution[i][j] > 0:
                        total += solution[i][j]
                    if j < width-1 and solution[i][j+1] > 0 and solution[i][j] > 0:
                        total += solution[i][j]
                    # Count vertical bridges
                    if i > 0 and solution[i-1][j] > 0 and solution[i][j] > 0:
                        total += solution[i][j]
                    if i < height-1 and solution[i+1][j] > 0 and solution[i][j] > 0:
                        total += solution[i][j]
                    
                    if total != puzzle[i][j]:
                        valid = False
                        break
            if not valid:
                break
        
        if valid:
            return solution
    
    return None