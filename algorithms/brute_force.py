import numpy as np
import time
from itertools import combinations, product

class BruteForceSolver:
    def __init__(self, grid):
        self.grid = grid
        self.rows, self.cols = self.grid.shape
        self.islands = self._find_islands()
        self.bridges = self._find_potential_bridges()
    
    def _find_islands(self):
        islands = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i, j] > 0:
                    islands.append((i, j, self.grid[i, j]))
        return islands
    
    def _find_potential_bridges(self):
        bridges = {'H': [], 'V': []}
        
        # Horizontal bridges
        for i in range(self.rows):
            cols = [j for j in range(self.cols) if self.grid[i, j] > 0]
            for j1, j2 in combinations(cols, 2):
                if j2 > j1 + 1 and all(self.grid[i, k] == 0 for k in range(j1+1, j2)):
                    bridges['H'].append((i, j1, i, j2))
        
        # Vertical bridges
        for j in range(self.cols):
            rows = [i for i in range(self.rows) if self.grid[i, j] > 0]
            for i1, i2 in combinations(rows, 2):
                if i2 > i1 + 1 and all(self.grid[k, j] == 0 for k in range(i1+1, i2)):
                    bridges['V'].append((i1, j, i2, j))
        
        return bridges
    
    def solve(self):
        start_time = time.time()
        
        # Convert bridges to list of all possible options
        all_bridges = []
        for bridge in self.bridges['H'] + self.bridges['V']:
            all_bridges.append(bridge)
        
        # Generate all possible combinations (0=no bridge, 1=single, 2=double)
        for combo in product([0, 1, 2], repeat=len(all_bridges)):
            solution = self._create_solution(all_bridges, combo)
            if self._is_valid_solution(solution):
                return solution, time.time() - start_time
        
        return None, time.time() - start_time
    
    def _create_solution(self, bridges, combo):
        solution = np.full_like(self.grid, '0', dtype='U2')
        
        # Mark islands
        for i, j, num in self.islands:
            solution[i, j] = str(num)
        
        # Mark bridges
        for (i1, j1, i2, j2), count in zip(bridges, combo):
            if count == 0:
                continue
                
            if i1 == i2:  # Horizontal bridge
                for k in range(j1+1, j2):
                    solution[i1, k] = '-' if count == 1 else '='
            else:  # Vertical bridge
                for k in range(i1+1, i2):
                    solution[k, j1] = '|' if count == 1 else '$'
        
        return solution
    
    def _is_valid_solution(self, solution):
        # Check if all islands have correct number of bridges
        for i, j, num in self.islands:
            count = 0
            
            # Check horizontal bridges to the left
            k = j - 1
            while k >= 0 and solution[i, k] in ['-', '=']:
                if solution[i, k] == '-':
                    count += 1
                else:
                    count += 2
                k -= 1
            
            # Check horizontal bridges to the right
            k = j + 1
            while k < self.cols and solution[i, k] in ['-', '=']:
                if solution[i, k] == '-':
                    count += 1
                else:
                    count += 2
                k += 1
            
            # Check vertical bridges above
            k = i - 1
            while k >= 0 and solution[k, j] in ['|', '$']:
                if solution[k, j] == '|':
                    count += 1
                else:
                    count += 2
                k -= 1
            
            # Check vertical bridges below
            k = i + 1
            while k < self.rows and solution[k, j] in ['|', '$']:
                if solution[k, j] == '|':
                    count += 1
                else:
                    count += 2
                k += 1
            
            if count != num:
                return False
        
        return True