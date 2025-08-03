class HashiBoard:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.islands = self._find_islands()
        self.bridges = []
        
    def _find_islands(self):
        islands = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] > 0:
                    islands.append((i, j, self.grid[i][j]))
        return islands
    
    def is_valid_position(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def is_island(self, row, col):
        return self.is_valid_position(row, col) and self.grid[row][col] > 0
    
    def get_island_value(self, row, col):
        return self.grid[row][col] if self.is_island(row, col) else 0
    
    def can_add_bridge(self, start, end, bridge_type):
        # Check if bridge can be added between start and end islands
        if start == end:
            return False
            
        # Check if islands are aligned horizontally or vertically
        if start[0] != end[0] and start[1] != end[1]:
            return False
            
        # Check if there's already a bridge between these islands
        for bridge in self.bridges:
            if (bridge['start'] == start and bridge['end'] == end) or \
               (bridge['start'] == end and bridge['end'] == start):
                if bridge['type'] == bridge_type:
                    return False
                if bridge['count'] >= 2:
                    return False
                    
        # Check path doesn't cross other islands or bridges
        if start[0] == end[0]:  # Horizontal bridge
            row = start[0]
            min_col = min(start[1], end[1])
            max_col = max(start[1], end[1])
            
            # Check for islands in between
            for col in range(min_col + 1, max_col):
                if self.is_island(row, col):
                    return False
                    
            # Check for crossing bridges
            for bridge in self.bridges:
                if bridge['start'][0] != bridge['end'][0]:  # Vertical bridge
                    b_col = bridge['start'][1]
                    b_min_row = min(bridge['start'][0], bridge['end'][0])
                    b_max_row = max(bridge['start'][0], bridge['end'][0])
                    if b_min_row < row < b_max_row and min_col < b_col < max_col:
                        return False
                        
        else:  # Vertical bridge
            col = start[1]
            min_row = min(start[0], end[0])
            max_row = max(start[0], end[0])
            
            # Check for islands in between
            for row in range(min_row + 1, max_row):
                if self.is_island(row, col):
                    return False
                    
            # Check for crossing bridges
            for bridge in self.bridges:
                if bridge['start'][1] != bridge['end'][1]:  # Horizontal bridge
                    b_row = bridge['start'][0]
                    b_min_col = min(bridge['start'][1], bridge['end'][1])
                    b_max_col = max(bridge['start'][1], bridge['end'][1])
                    if b_min_col < col < b_max_col and min_row < b_row < max_row:
                        return False
                        
        return True
    
    def add_bridge(self, start, end, bridge_type):
        if not self.can_add_bridge(start, end, bridge_type):
            return False
            
        # Find if bridge already exists (to increment count)
        for bridge in self.bridges:
            if (bridge['start'] == start and bridge['end'] == end) or \
               (bridge['start'] == end and bridge['end'] == start):
                bridge['count'] += 1
                bridge['type'] = bridge_type
                return True
                
        # Add new bridge
        self.bridges.append({
            'start': start,
            'end': end,
            'type': bridge_type,
            'count': 1
        })
        return True
    
    def is_solved(self):
        # Check all islands have correct number of bridges
        island_bridges = {island: 0 for island in self.islands}
        for bridge in self.bridges:
            island_bridges[(bridge['start'][0], bridge['start'][1], 
                          self.get_island_value(bridge['start'][0], bridge['start'][1]))] += bridge['count']
            island_bridges[(bridge['end'][0], bridge['end'][1], 
                          self.get_island_value(bridge['end'][0], bridge['end'][1]))] += bridge['count']
        
        for island in self.islands:
            if island_bridges.get(island, 0) != island[2]:
                return False
                
        # Check all islands are connected (single connected component)
        if not self.islands:
            return True
            
        visited = set()
        stack = [self.islands[0]]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            
            # Find all connected islands through bridges
            for bridge in self.bridges:
                if (bridge['start'][0], bridge['start'][1]) == (current[0], current[1]):
                    end_island = next((i for i in self.islands if (i[0], i[1]) == (bridge['end'][0], bridge['end'][1])), None)
                    if end_island and end_island not in visited:
                        stack.append(end_island)
                elif (bridge['end'][0], bridge['end'][1]) == (current[0], current[1]):
                    start_island = next((i for i in self.islands if (i[0], i[1]) == (bridge['start'][0], bridge['start'][1])), None)
                    if start_island and start_island not in visited:
                        stack.append(start_island)
        
        return len(visited) == len(self.islands)
    
    def to_output_grid(self):
            output = [['0' for _ in range(self.cols)] for _ in range(self.rows)]
            
            # Mark islands
            for island in self.islands:
                output[island[0]][island[1]] = str(island[2])
                
            # Mark bridges
            for bridge in self.bridges:
                if bridge['start'][0] == bridge['end'][0]:  # Horizontal bridge
                    row = bridge['start'][0]
                    start_col = min(bridge['start'][1], bridge['end'][1])
                    end_col = max(bridge['start'][1], bridge['end'][1])
                    
                    for col in range(start_col + 1, end_col):
                        if bridge['count'] == 1:
                            output[row][col] = '-'
                        else:
                            output[row][col] = '='
                            
                else:  # Vertical bridge
                    col = bridge['start'][1]
                    start_row = min(bridge['start'][0], bridge['end'][0])
                    end_row = max(bridge['start'][0], bridge['end'][0])
                    
                    for row in range(start_row + 1, end_row):
                        if bridge['count'] == 1:
                            output[row][col] = '|'
                        else:
                            output[row][col] = '$'
            
            return output
    
    def is_valid_solution(self):
        # Check all islands have correct number of bridges
        island_counts = {}
        for island in self.islands:
            island_counts[(island[0], island[1])] = 0

        for bridge in self.bridges:
            start = (bridge['start'][0], bridge['start'][1])
            end = (bridge['end'][0], bridge['end'][1])
            island_counts[start] += bridge['count']
            island_counts[end] += bridge['count']

        for island in self.islands:
            pos = (island[0], island[1])
            if island_counts.get(pos, 0) != island[2]:
                return False

        # Check all islands are connected
        return self.is_fully_connected()

    def is_fully_connected(self):
        if not self.islands:
            return True

        visited = set()
        stack = [self.islands[0][:2]]  # (row, col)

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)

            # Find connected islands through bridges
            for bridge in self.bridges:
                start = (bridge['start'][0], bridge['start'][1])
                end = (bridge['end'][0], bridge['end'][1])
                
                if current == start and end not in visited:
                    stack.append(end)
                elif current == end and start not in visited:
                    stack.append(start)

        return len(visited) == len(self.islands)
    
    def __str__(self):
        output_grid = self.to_output_grid()
        return '\n'.join([' '.join(map(str, row)) for row in output_grid])