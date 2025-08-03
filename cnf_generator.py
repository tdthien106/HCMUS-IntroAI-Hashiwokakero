from itertools import combinations, product
from collections import defaultdict

class CNFGenerator:
    def __init__(self, board):
        self.board = board
        self.variables = {}
        self.clauses = []
        self.next_var = 1
        self.island_pos_to_idx = {(x,y): i for i, (x,y,_) in enumerate(board.islands)}
        
    def generate_cnf(self):
        self._create_variables()
        self._add_bridge_constraints()
        self._add_island_constraints()
        self._add_crossing_constraints()
        return self.clauses, self.variables

    def _create_variables(self):
        for i, (x1, y1, _) in enumerate(self.board.islands):
            for j, (x2, y2, _) in enumerate(self.board.islands[i+1:], i+1):
                if self._can_connect((x1,y1), (x2,y2)):
                    self.variables[(i,j,1)] = self.next_var  # Single bridge
                    self.next_var += 1
                    self.variables[(i,j,2)] = self.next_var  # Double bridge
                    self.next_var += 1

    def _can_connect(self, a, b):
        if a[0] == b[0]:  # Horizontal
            y_min, y_max = sorted([a[1], b[1]])
            return all(not self.board.is_island(a[0], y) for y in range(y_min+1, y_max))
        elif a[1] == b[1]:  # Vertical
            x_min, x_max = sorted([a[0], b[0]])
            return all(not self.board.is_island(x, a[1]) for x in range(x_min+1, x_max))
        return False

    def _add_bridge_constraints(self):
        for (i,j,c), var in self.variables.items():
            if c == 2:  # Double bridge
                single_var = self.variables[(i,j,1)]
                self.clauses.append([-var, single_var])  # Double → Single
                self.clauses.append([-var, -single_var])  # Not both

    def _add_island_constraints(self):
        for idx, (x,y,demand) in enumerate(self.board.islands):
            bridge_vars = []
            for (i,j,c), var in self.variables.items():
                if i == idx or j == idx:
                    bridge_vars.append((var, c))
            
            self._add_exact_quantity_constraint(bridge_vars, demand)

    def _add_exact_quantity_constraint(self, vars_weights, k):
        """Ràng buộc chính xác số bridges cho đảo"""
        if not vars_weights:
            if k == 0:
                return
            self.clauses.append([])  # Unsatisfiable
            return

        # At-Least-K (ít nhất k bridges)
        self._add_at_least_k(vars_weights, k)
        
        # At-Most-K (nhiều nhất k bridges)
        self._add_at_most_k(vars_weights, k)

        # Bổ sung ràng buộc cho các đảo yêu cầu nhiều bridges
        if k >= 2:
            # Đảm bảo có ít nhất 1 bridge kép hoặc 2 bridge đơn
            single_vars = [var for var, w in vars_weights if w == 1]
            double_vars = [var for var, w in vars_weights if w == 2]
            
            if double_vars:
                # Có thể chọn 1 bridge kép
                self.clauses.append(double_vars)
            if len(single_vars) >= 2:
                # Hoặc chọn 2 bridge đơn
                for v1, v2 in combinations(single_vars, 2):
                    self.clauses.append([v1, v2])

    def _add_at_least_k(self, vars_weights, k):
        """Sequential counter encoding cho ≥ k"""
        if not vars_weights or k <= 0:
            return
            
        s_vars = []
        for _ in range(len(vars_weights)):
            s_vars.append(self.next_var)
            self.next_var += 1
        
        for i, ((var, w), s_i) in enumerate(zip(vars_weights, s_vars)):
            if i == 0:
                if w >= k:
                    self.clauses.append([var])
                else:
                    self.clauses.append([-var, s_i])
            else:
                s_prev = s_vars[i-1]
                if w >= k:
                    self.clauses.append([var])
                else:
                    self.clauses.append([-var, s_i])
                    self.clauses.append([-s_prev, s_i])
                    if w == 1:
                        self.clauses.append([-s_prev, -var, s_i])
        
        if vars_weights[-1][1] < k:
            self.clauses.append([-s_vars[-1]])

    def _add_at_most_k(self, vars_weights, k):
        """Pairwise encoding cho ≤ k"""
        if not vars_weights:
            return
            
        # Chỉ xét các biến có trọng số
        weighted_vars = [(v, w) for v, w in vars_weights if w > 0]
        
        # Tổng trọng số tối đa
        total = sum(w for _, w in weighted_vars)
        if k >= total:
            return
            
        # Tạo tổ hợp các biến có tổng trọng số > k
        for r in range(1, len(weighted_vars)+1):
            for subset in combinations(weighted_vars, r):
                vars_subset, weights_subset = zip(*subset)
                if sum(weights_subset) > k:
                    self.clauses.append([-v for v in vars_subset])

    def _add_crossing_constraints(self):
        """Ngăn các bridge cắt nhau"""
        bridges = [(i,j) for (i,j,c) in self.variables if c == 1]
        for (i1,j1), (i2,j2) in combinations(bridges, 2):
            if self._do_bridges_cross(i1,j1,i2,j2):
                var1 = self.variables[(i1,j1,1)]
                var2 = self.variables[(i2,j2,1)]
                self.clauses.append([-var1, -var2])

    def _do_bridges_cross(self, i1,j1,i2,j2):
        a = self.board.islands[i1]
        b = self.board.islands[j1]
        c = self.board.islands[i2]
        d = self.board.islands[j2]
        
        seg1 = ((a[0],a[1]), (b[0],b[1]))
        seg2 = ((c[0],c[1]), (d[0],d[1]))
        return self._segments_cross(seg1, seg2)

    def _segments_cross(self, seg1, seg2):
        (x1,y1), (x2,y2) = seg1
        (x3,y3), (x4,y4) = seg2
        
        def ccw(a,b,c):
            return (c[1]-a[1])*(b[0]-a[0]) > (b[1]-a[1])*(c[0]-a[0])
            
        intersect = ccw((x1,y1),(x3,y3),(x4,y4)) != ccw((x2,y2),(x3,y3),(x4,y4)) and \
                   ccw((x1,y1),(x2,y2),(x3,y3)) != ccw((x1,y1),(x2,y2),(x4,y4))
        
        return intersect and not self._share_endpoint(seg1, seg2)

    def _share_endpoint(self, seg1, seg2):
        return any(p1 == p2 for p1 in seg1 for p2 in seg2)
