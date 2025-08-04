import time
from pysat.solvers import Glucose4
from pysat.formula import CNF

from cnf_generator import CNFGenerator

class PySatSolver:
    def __init__(self, board):
        self.board = board
        self.cnf_generator = CNFGenerator(board)
        self.timeout = 10  # seconds
        
    def solve(self):
        try:
            clauses, variables = self.cnf_generator.generate_cnf()
            print(f"Generated {len(clauses)} clauses and {len(variables)} variables")
            
            cnf = CNF()
            for clause in clauses:
                cnf.append(clause)
                
            start_time = time.time()
            with Glucose4(bootstrap_with=cnf) as solver:
                while True:
                    if solver.solve(assumptions=[]):
                        model = solver.get_model()
                        solved_board = self.board.copy()
                        solved_board.bridges = []
                        assignments = {abs(var): var > 0 for var in model}
                        for (i, j, c), var in sorted(variables.items(), key=lambda x: (-x[0][2], x[0][0], x[0][1])):
                            if assignments.get(var, False):
                                island1 = solved_board.islands[i]
                                island2 = solved_board.islands[j]
                                start = (island1[0], island1[1])
                                end = (island2[0], island2[1])
                                btype = 'h' if start[0] == end[0] else 'v'
                                for _ in range(c):
                                    solved_board.add_bridge(start, end, btype)
                        # Always return the board, regardless of validity
                        print(f"SAT solution returned in {time.time()-start_time:.2f}s")
                        return solved_board
                    if time.time() - start_time > self.timeout:
                        break
            return None
        except Exception as e:
            print(f"Solver error: {str(e)}")
            return None
