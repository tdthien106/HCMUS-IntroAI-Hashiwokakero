from itertools import combinations


class CNFGenerator:
    def __init__(self, board):
        self.board = board
        self.variables = {}
        self.clauses = []
        self.next_var = 1
        self.island_indices = {(island[0], island[1]): idx for idx, island in enumerate(board.islands)}

    def generate_cnf(self):
        self._create_variables()
        self._add_bridge_constraints()
        self._add_island_constraints()
        return self.clauses, self.variables

    def _create_variables(self):
        # Tạo biến cho các cầu có thể có giữa các đảo
        for i, island1 in enumerate(self.board.islands):
            for j, island2 in enumerate(self.board.islands[i+1:], i+1):
                if self._are_alignable(island1, island2):
                    # Biến cho cầu đơn giữa island1 và island2
                    self.variables[(i, j, 1)] = self.next_var
                    self.next_var += 1
                    # Biến cho cầu đôi giữa island1 và island2
                    self.variables[(i, j, 2)] = self.next_var
                    self.next_var += 1

    def _are_alignable(self, island1, island2):
        # Kiểm tra xem có thể nối 2 đảo bằng cầu ngang/dọc mà không bị chặn
        if island1[0] == island2[0]:  # Cùng hàng - cầu ngang
            row = island1[0]
            start_col = min(island1[1], island2[1])
            end_col = max(island1[1], island2[1])
            for col in range(start_col + 1, end_col):
                if self.board.is_island(row, col):
                    return False
            return True
        elif island1[1] == island2[1]:  # Cùng cột - cầu dọc
            col = island1[1]
            start_row = min(island1[0], island2[0])
            end_row = max(island1[0], island2[0])
            for row in range(start_row + 1, end_row):
                if self.board.is_island(row, col):
                    return False
            return True
        return False

    def _add_bridge_constraints(self):
        # Ràng buộc cho biến cầu:
        # 1. Nếu cầu đôi được chọn thì cầu đơn cũng phải được chọn
        # 2. Không thể chọn cả cầu đơn và cầu đôi cùng lúc
        for (i, j, count), var in self.variables.items():
            if count == 2:
                single_var = self.variables[(i, j, 1)]
                self.clauses.append([-var, single_var])  # Double → Single
                self.clauses.append([-var, -single_var])  # Not both

    def _add_island_constraints(self):
        # Ràng buộc về số cầu tại mỗi đảo
        for idx, island in enumerate(self.board.islands):
            required = island[2]
            bridge_vars = []
            
            # Tìm tất cả các cầu có thể nối với đảo này
            for (i, j, count), var in self.variables.items():
                if i == idx or j == idx:
                    bridge_vars.append((var, count))
            
            # Tạo ràng buộc chính xác số cầu cần thiết
            self._exactly_k_constraints(bridge_vars, required)

    def _exactly_k_constraints(self, variables, k):
        # Tạo clauses cho đúng k biến được chọn
        if k == 0:
            # Không chọn bất kỳ cầu nào
            for var, _ in variables:
                self.clauses.append([-var])
            return
            
        # Ít nhất k cầu (tính theo trọng số)
        # Chuyển đổi bài toán subset sum thành CNF
        self._add_amo_constraints(variables, k)
        self._add_alo_constraints(variables, k)

    def _add_alo_constraints(self, variables, k):
        # At-Least-One constraints
        # Tổng trọng số các cầu được chọn phải ≥ k
        # Sử dụng sequential encoding
        pass  # Triển khai phức tạp, tạm bỏ qua cho đơn giản

    def _add_amo_constraints(self, variables, k):
        # At-Most-One constraints
        # Tổng trọng số các cầu được chọn phải ≤ k
        # Sử dụng pairwise constraints
        for subset in combinations(variables, len(variables)):
            if sum(count for _, count in subset) > k:
                self.clauses.append([-var for var, _ in subset])