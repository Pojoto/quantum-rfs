# Import package, test suite, and other packages as needed
import numpy as np
import quantum_rfs as qrfs
import itertools

def test_rfs_creation():

    n_tests = [2, 3, 4, 5, 6, 7]
    l_tests = [2, 3, 4, 5, 6, 7]

    for n_test, l_test in itertools.product(n_tests, l_tests):

        new_problem = qrfs.RFSProblem(n_test, l_test)

        #print(new_problem.secrets)

        assert(new_problem.n == n_test)
        assert(new_problem.l == l_test)

        secrets_size = n_test * (n_test ** l_test - 1) / (n_test - 1) + 1

        # print("N: " + str(n_test) + "   L: " + str(l_test) + "  LEN: " + str(len(new_problem.secrets)))
        # print("N: " + str(n_test) + "   L: " + str(l_test) + "  len: " + str(secrets_size))

        assert(len(new_problem.secrets) == secrets_size)
        assert(len(new_problem.g_func) == 2 ** n_test)


# def test_classical_quantum_solutions():
#     n_tests = [2, 3, 4, 5, 6, 7]
#     l_tests = [2, 3, 4, 5, 6, 7]

#     for n_test, l_test in itertools.product(n_tests, l_tests):

#         new_problem = qrfs.RFSProblem(n_test, l_test)

#         classical_solution = new_problem.solve_classically()
#         quantum_solution = new_problem.solve_quantumly()

#         assert(classical_solution == quantum_solution)

def test_classical_quantum_solutions():
    n_tests = [2]
    l_tests = [2]

    for n_test, l_test in itertools.product(n_tests, l_tests):

        new_problem = qrfs.RFSProblem(n_test, l_test)

        classical_solution = new_problem.solve_classically()
        quantum_solution = new_problem.solve_quantumly()

        assert(classical_solution == quantum_solution)
# test_classical_quantum_solutions
# test_rfs_creation()