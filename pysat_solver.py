from pysat.solvers import Solver
from pysat.formula import CNF

from cnf_generator import CNFGenerator

class PySatSolver:
    def __init__(self, board):
        self.board = board
        self.cnf_generator = CNFGenerator(board)
        
    def solve(self):
        clauses, variables = self.cnf_generator.generate_cnf()
        cnf = CNF()
        
        # Thêm clauses vào CNF
        for clause in clauses:
            cnf.append(clause)
            
        # Giải bằng PySAT
        with Solver(bootstrap_with=cnf) as solver:
            if solver.solve():
                model = solver.get_model()
                self._apply_solution(model, variables)
                return True
        return False
        
    def _apply_solution(self, model, variables):
        # Áp dụng solution lên board
        assignments = {abs(var): var > 0 for var in model}
        
        for (i, j, count), var in variables.items():
            if assignments.get(var, False):
                island1 = self.board.islands[i]
                island2 = self.board.islands[j]
                start = (island1[0], island1[1])
                end = (island2[0], island2[1])
                
                bridge_type = 'h' if start[0] == end[0] else 'v'
                for _ in range(count):
                    self.board.add_bridge(start, end, bridge_type)