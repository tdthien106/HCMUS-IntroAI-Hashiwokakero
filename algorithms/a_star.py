from itertools import combinations
import numpy as np
import time
import heapq
from copy import deepcopy

class AStarSolver:
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
        
        # Priority queue: (f_score, state_id, g_score, state)
        open_set = []
        state_id = 0
        visited = set()
        
        # Initial state
        initial_state = {
            'bridges': tuple([0] * (len(self.bridges['H']) + len(self.bridges['V']))),
            'grid': self._create_empty_grid()
        }
        
        # Calculate initial heuristic
        h_score = self._heuristic(initial_state)
        g_score = 0
        f_score = g_score + h_score
        
        heapq.heappush(open_set, (f_score, state_id, g_score, initial_state))
        state_id += 1
        
        while open_set:
            current_f, _, current_g, current_state = heapq.heappop(open_set)
            
            # Skip if already visited
            state_key = self._get_state_key(current_state)
            if state_key in visited:
                continue
            visited.add(state_key)
            
            if self._is_goal_state(current_state):
                return self._create_solution(current_state), time.time() - start_time
            
            for next_state in self._get_next_states(current_state):
                state_key = self._get_state_key(next_state)
                if state_key in visited:
                    continue
                
                new_g = current_g + 1
                new_h = self._heuristic(next_state)
                new_f = new_g + new_h
                
                heapq.heappush(open_set, (new_f, state_id, new_g, next_state))
                state_id += 1
        
        return None, time.time() - start_time
    
    def _get_state_key(self, state):
        """Create a unique key for the state to avoid duplicates"""
        return (state['bridges'], tuple(map(tuple, state['grid'])))
    
    def _create_empty_grid(self):
        """Create initial grid with islands marked"""
        grid = np.full_like(self.grid, '0', dtype='U2')
        for i, j, num in self.islands:
            grid[i, j] = str(num)
        return grid
    
    def _get_next_states(self, current_state):
        next_states = []
        all_bridges = self.bridges['H'] + self.bridges['V']
        
        for i, bridge in enumerate(all_bridges):
            if current_state['bridges'][i] < 2:  # Can add more bridges
                new_state = {
                    'bridges': list(current_state['bridges']),
                    'grid': current_state['grid'].copy()
                }
                new_state['bridges'][i] += 1
                new_state['bridges'] = tuple(new_state['bridges'])
                
                # Update grid
                i1, j1, i2, j2 = bridge
                if i1 == i2:  # Horizontal
                    for k in range(j1+1, j2):
                        new_state['grid'][i1, k] = '-' if new_state['bridges'][i] == 1 else '='
                else:  # Vertical
                    for k in range(i1+1, i2):
                        new_state['grid'][k, j1] = '|' if new_state['bridges'][i] == 1 else '$'
                
                if self._is_valid_state(new_state):
                    next_states.append(new_state)
        
        return next_states
    
    def _is_valid_state(self, state):
        # Similar to previous implementations
        for i, j, num in self.islands:
            count = 0
            
            # Check horizontal bridges
            k = j - 1
            while k >= 0 and state['grid'][i, k] in ['-', '=']:
                if state['grid'][i, k] == '-':
                    count += 1
                else:
                    count += 2
                k -= 1
            
            k = j + 1
            while k < self.cols and state['grid'][i, k] in ['-', '=']:
                if state['grid'][i, k] == '-':
                    count += 1
                else:
                    count += 2
                k += 1
            
            # Check vertical bridges
            k = i - 1
            while k >= 0 and state['grid'][k, j] in ['|', '$']:
                if state['grid'][k, j] == '|':
                    count += 1
                else:
                    count += 2
                k -= 1
            
            k = i + 1
            while k < self.rows and state['grid'][k, j] in ['|', '$']:
                if state['grid'][k, j] == '|':
                    count += 1
                else:
                    count += 2
                k += 1
            
            if count > num:
                return False
        
        return True
    
    def _is_goal_state(self, state):
        # Check if all islands have correct number of bridges
        for i, j, num in self.islands:
            count = 0
            
            # Check horizontal bridges
            k = j - 1
            while k >= 0 and state['grid'][i, k] in ['-', '=']:
                if state['grid'][i, k] == '-':
                    count += 1
                else:
                    count += 2
                k -= 1
            
            k = j + 1
            while k < self.cols and state['grid'][i, k] in ['-', '=']:
                if state['grid'][i, k] == '-':
                    count += 1
                else:
                    count += 2
                k += 1
            
            # Check vertical bridges
            k = i - 1
            while k >= 0 and state['grid'][k, j] in ['|', '$']:
                if state['grid'][k, j] == '|':
                    count += 1
                else:
                    count += 2
                k -= 1
            
            k = i + 1
            while k < self.rows and state['grid'][k, j] in ['|', '$']:
                if state['grid'][k, j] == '|':
                    count += 1
                else:
                    count += 2
                k += 1
            
            if count != num:
                return False
        
        return True
    
    def _heuristic(self, state):
        # Heuristic: sum of remaining bridges needed
        total_remaining = 0
        for i, j, num in self.islands:
            count = 0
            
            # Count existing bridges
            k = j - 1
            while k >= 0 and state['grid'][i, k] in ['-', '=']:
                if state['grid'][i, k] == '-':
                    count += 1
                else:
                    count += 2
                k -= 1
            
            k = j + 1
            while k < self.cols and state['grid'][i, k] in ['-', '=']:
                if state['grid'][i, k] == '-':
                    count += 1
                else:
                    count += 2
                k += 1
            
            k = i - 1
            while k >= 0 and state['grid'][k, j] in ['|', '$']:
                if state['grid'][k, j] == '|':
                    count += 1
                else:
                    count += 2
                k -= 1
            
            k = i + 1
            while k < self.rows and state['grid'][k, j] in ['|', '$']:
                if state['grid'][k, j] == '|':
                    count += 1
                else:
                    count += 2
                k += 1
            
            total_remaining += max(0, num - count)
        
        return total_remaining