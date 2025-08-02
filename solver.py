import numpy as np
import time
from pysat.solvers import Glucose4
from itertools import combinations
from algorithms.brute_force import BruteForceSolver
from algorithms.backtracking import BacktrackingSolver
from algorithms.a_star import AStarSolver

class HashiwokakeroSolver:
    def __init__(self, grid):
        self.grid = grid
        self.rows, self.cols = self.grid.shape
        self.islands = self._find_islands()
        self.bridges = self._find_potential_bridges()
        self.variables = self._create_variables()
        self.cnf = []
    
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
    
    def _create_variables(self):
        variables = {}
        var_count = 1
        
        for (i1, j1, i2, j2) in self.bridges['H']:
            for b in [1, 2]:  # single or double bridge
                variables[(i1, j1, i2, j2, 'H', b)] = var_count
                var_count += 1
        
        for (i1, j1, i2, j2) in self.bridges['V']:
            for b in [1, 2]:  # single or double bridge
                variables[(i1, j1, i2, j2, 'V', b)] = var_count
                var_count += 1
        
        return variables
    
    def _island_bridge_map(self):
        island_bridges = {island: [] for island in self.islands}
        
        for (i1, j1, i2, j2, dir, b), var in self.variables.items():
            island1 = (i1, j1)
            island2 = (i2, j2)
            for island in self.islands:
                if (island[0], island[1]) == island1 or (island[0], island[1]) == island2:
                    island_bridges[island].append(var)
        
        return island_bridges
    
    def generate_cnf(self):
        island_bridges = self._island_bridge_map()
        
        # 1. Island constraints: sum of bridges must equal island number
        for island, bridges in island_bridges.items():
            i, j, num = island
            bridge_vars = [var for var in bridges]
            
            # At least one bridge must be selected if num > 0
            if num > 0:
                self.cnf.append(bridge_vars)
            
            # Generate all possible combinations that sum to the island number
            valid_combinations = []
            for r in range(1, len(bridge_vars)+1):
                for combo in combinations(bridge_vars, r):
                    # Simplified check - actual implementation would need to track bridge counts
                    if len(combo) <= num <= 2*len(combo):
                        valid_combinations.append(list(combo))
            
            for combo in valid_combinations:
                self.cnf.append(combo)
        
        return self.cnf
    
    def solve(self):
        """Solve using SAT solver"""
        start_time = time.time()
        self.generate_cnf()
        
        with Glucose4(bootstrap_with=self.cnf) as solver:
            if solver.solve():
                model = solver.get_model()
                solution = self._interpret_solution(model)
                return solution, time.time() - start_time
            return None, time.time() - start_time
    
    def _interpret_solution(self, model):
        solution = np.full_like(self.grid, '0', dtype='U2')
        
        # Mark islands
        for i, j, num in self.islands:
            solution[i, j] = str(num)
        
        # Mark bridges based on positive variables in the model
        for (i1, j1, i2, j2, dir, b), var in self.variables.items():
            if var in model:
                if dir == 'H':  # Horizontal bridge
                    for k in range(j1+1, j2):
                        solution[i1, k] = '-' if b == 1 else '='
                elif dir == 'V':  # Vertical bridge
                    for k in range(i1+1, i2):
                        solution[k, j1] = '|' if b == 1 else '$'
        
        return solution
    
    def compare_algorithms(self):
        """Compare all algorithms and return their execution times"""
        results = {}
        
        # SAT Solver
        try:
            sat_solution, sat_time = self.solve()
            results['SAT'] = sat_time
        except Exception as e:
            print(f"SAT Error: {str(e)}")
            results['SAT'] = float('inf')
        
        # Brute Force
        try:
            bf = BruteForceSolver(self.grid)
            bf_solution, bf_time = bf.solve()
            results['Brute Force'] = bf_time
        except Exception as e:
            print(f"Brute Force Error: {str(e)}")
            results['Brute Force'] = float('inf')
        
        # Backtracking
        try:
            bt = BacktrackingSolver(self.grid)
            bt_solution, bt_time = bt.solve()
            results['Backtracking'] = bt_time
        except Exception as e:
            print(f"Backtracking Error: {str(e)}")
            results['Backtracking'] = float('inf')
        
        # A* Search
        try:
            astar = AStarSolver(self.grid)
            astar_solution, astar_time = astar.solve()
            results['A*'] = astar_time
        except Exception as e:
            print(f"A* Error: {str(e)}")
            results['A*'] = float('inf')
        
        return results