import time
from pysat.solvers import Glucose4
from pysat.formula import CNF

from cnf_generator import CNFGenerator

class PySatSolver:
    def __init__(self, board):
        self.board = board
        self.cnf_generator = CNFGenerator(board)
        self.timeout = 0.7  # seconds
        
    def solve(self):
        try:
            clauses, variables = self.cnf_generator.generate_cnf()
            print(f"Generated {len(clauses)} clauses and {len(variables)} variables")
            
            cnf = CNF()
            for clause in clauses:
                cnf.append(clause)
                
            start_time = time.time()
            with Glucose4(bootstrap_with=cnf) as solver:
                # Triển khai timeout thủ công
                while True:
                    if solver.solve(assumptions=[]):
                        model = solver.get_model()
                        self._apply_solution(model, variables)
                        if self.board.is_valid_solution():
                            print(f"Solution found in {time.time()-start_time:.2f}s")
                            return True
                        break
                    
                    if time.time() - start_time > self.timeout:
                        #print("Timeout reached")
                        break
            
            #print("No valid solution found")
            return False
            
        except Exception as e:
            print(f"Solver error: {str(e)}")
            return False
        
    def _apply_solution(self, model, variables):
        assignments = {abs(var): var > 0 for var in model}
        
        # Thêm bridge kép trước
        for (i,j,c), var in sorted(variables.items(), 
                                 key=lambda x: (-x[0][2], x[0][0], x[0][1])):
            if assignments.get(var, False):
                self._add_bridge(i, j, c)
    
    def _add_bridge(self, i, j, count):
        island1 = self.board.islands[i]
        island2 = self.board.islands[j]
        start = (island1[0], island1[1])
        end = (island2[0], island2[1])
        btype = 'h' if start[0] == end[0] else 'v'
        
        for _ in range(count):
            if not self.board.add_bridge(start, end, btype):
                print(f"Failed to add bridge {count}x between {start} and {end}")
                return False
        return True
