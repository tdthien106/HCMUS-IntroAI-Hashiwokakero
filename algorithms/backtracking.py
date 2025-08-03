from copy import deepcopy

def solve(puzzle):
    """Solve using backtracking"""
    height = len(puzzle)
    width = len(puzzle[0]) if height > 0 else 0
    
    # Find all islands
    islands = []
    for i in range(height):
        for j in range(width):
            if puzzle[i][j] > 0:
                islands.append((i, j, puzzle[i][j]))
    
    # Initialize solution
    solution = [[0 for _ in range(width)] for _ in range(height)]
    
    if backtrack(islands, 0, solution, puzzle):
        return solution
    return None

def backtrack(islands, index, solution, puzzle):
    """Recursive backtracking function"""
    if index == len(islands):
        return True
    
    i, j, required = islands[index]
    
    # Find possible connections
    connections = []
    for other_i, other_j, other_req in islands[index+1:]:
        if i == other_i or j == other_j:  # Same row or column
            connections.append((other_i, other_j))
    
    # Try all possible connections
    for other_i, other_j in connections:
        for count in [1, 2]:  # Try single and double bridges
            if is_valid_connection(i, j, other_i, other_j, count, solution, puzzle):
                # Apply the bridge
                apply_bridge(i, j, other_i, other_j, count, solution)
                
                if backtrack(islands, index + 1, solution, puzzle):
                    return True
                
                # Revert the bridge
                revert_bridge(i, j, other_i, other_j, count, solution)
    
    return False

def is_valid_connection(i1, j1, i2, j2, count, solution, puzzle):
    """Check if adding a bridge is valid"""
    # Check if bridge would exceed island capacity
    if (puzzle[i1][j1] < count or puzzle[i2][j2] < count):
        return False
    
    # Check if path is clear
    if i1 == i2:  # Horizontal
        for j in range(min(j1, j2) + 1, max(j1, j2)):
            if puzzle[i1][j] > 0:  # Another island in the way
                return False
            if solution[i1][j] + count > 2:  # Would exceed bridge limit
                return False
    else:  # Vertical
        for i in range(min(i1, i2) + 1, max(i1, i2)):
            if puzzle[i][j1] > 0:  # Another island in the way
                return False
            if solution[i][j1] + count > 2:  # Would exceed bridge limit
                return False
    
    return True

def apply_bridge(i1, j1, i2, j2, count, solution):
    """Add a bridge to the solution"""
    if i1 == i2:  # Horizontal
        for j in range(min(j1, j2), max(j1, j2) + 1):
            solution[i1][j] += count
    else:  # Vertical
        for i in range(min(i1, i2), max(i1, i2) + 1):
            solution[i][j1] += count

def revert_bridge(i1, j1, i2, j2, count, solution):
    """Remove a bridge from the solution"""
    if i1 == i2:  # Horizontal
        for j in range(min(j1, j2), max(j1, j2) + 1):
            solution[i1][j] -= count
    else:  # Vertical
        for i in range(min(i1, i2), max(i1, i2) + 1):
            solution[i][j1] -= count