from quantum_rfs.RFSProblem import *

new_problem = RFSProblem(2, 2)

print(new_problem)

print(new_problem.secrets)

new_problem.solve_classically()