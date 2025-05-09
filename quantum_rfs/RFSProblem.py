
from qiskit import QuantumCircuit
import random
import itertools
import qiskit_aer
import matplotlib.pyplot as plt

class RFSProblem:
    """
    Main class that describes a Recursive Fourier Sampling problem
    """
    def __init__(self, n, l):
        """
        Constructor for Recursive Fourier Sampling Problem (RFSProblem) objects. Populates the
        secrets and g function dictionaries, and gives back the A oracle that is later used.

        Parameters
        ----------
        n   : number
            There are 2^n children of each node
        l   : number
            Length or depth of tree
        """
        self.n = n
        self.l = l
        self.last_classical_call_count = 0
        self.last_quantum_call_count = 0

        self.secrets = {

        }

        self.A_oracle = {

        }

        self.g_func = self._g_func_create()

        self._g_secret_populate()


    def __str__(self):
        """
        Print dunder method to display the secrets of all the nodes in this problem.
        """
        string = str(self.secrets)
        return string



    def _g_func_create(self):
        """
        Creates a random 'g' function for the RFS problem

        Returns
        -------
        result  : dictionary
            The 'g' function dictionary which assigns n-bit strings to a single bit
        """
        bitstrings = [''.join(bits) for bits in itertools.product('01', repeat=self.n)]
        result = {b: random.choice('01') for b in bitstrings}
        return result
    

    def _g_secret_populate(self, node_id=()):
        """
        Recursive function that populates the secrets and 'g' function dictionaries in this object.

        Parameters
        -------
        node_id  : tuple
            The sequence of bitstrings that identifies each node in the graph. This is passed down recursively.

        Returns
        -------
        g_secret  : number
            The g(secret) of the current node
        """
        level = len(node_id)
        if level == self.l:
            secret = ''.join(random.choice('01') for _ in range(self.n))
            self.secrets[node_id] = secret
            self.A_oracle[node_id] = self.g_func[secret]
            return self.g_func[secret]


        curr_secret = ""
        for i in range(self.n):
            x = "0" * self.n
            x = x[:i] + "1" + x[i+1:]
            g_secret = self._g_secret_populate(node_id + (x,))
            curr_secret += g_secret

        self.secrets[node_id] = curr_secret

        return self.g_func[curr_secret]
        

    def _c_rfs(self, root_id):
        """
        Recursive function that solves this RFSProblem object classically, climbing up the tree.

        Parameters
        -------
        root_id  : tuple
            The sequence of bitstrings that identifies each node or root in the graph. This is passed down recursively.

        Returns
        -------
        g_secret  : number
            The g(secret) of the current node to be used recursively in the solution
        """
        self.last_classical_call_count += 1

        level = len(root_id)

        if level == self.l:
            return self.A_oracle[root_id]
        
        secret = ""
        for i in range(self.n):
            x = "0" * self.n
            x = x[:i] + "1" + x[i+1:]
            secret += self._c_rfs(root_id + (x,))

        g_secret = self.g_func[secret]
        if level == 0:
            print("Root Secret: " + secret)

        return g_secret


    def solve_classically(self):
        """
        This is the overarching function that calls the recursive classical solution.
        """
        self.last_classical_call_count = 0
        start_root_id = ()
        root_secret = self._c_rfs(start_root_id)
        # print(root_secret)
        # print(self.secrets[()])
        return root_secret




    def bernstein_vazirani_circuit(self, s):
        """
        This is the quantum circuit implementation of the Bernstein Vazirani solution to the RFS problem.

        Parameters
        -------
        s  : string
            Secret used to construct and check the solution

        Returns
        -------
        qc  : QuantumCircuit
            The quantum circuit of the Bernstein Vazirani solution to the problem.
        """
        n = len(s)
        qc = QuantumCircuit(n + 1, n)

        qc.x(n)       
        qc.h(n)       
        qc.h(range(n))  


        for i, bit in enumerate(s):
            if bit == '1':
                qc.cx(i, n)

        qc.h(range(n))    
        qc.measure(range(n), range(n))  

        return qc


    def solve_quantumly(self):
        """
        Overarching method that calls the recursion for the quantum solution.

        Returns
        -------
        g_secret  : number
            The g(secret) of the  root node (current node when recursive)
        """
        bitstrings = [''.join(p) for p in itertools.product('01', repeat=self.n)]
        s = self.secrets[()]

        qc = self.bernstein_vazirani_circuit(s)
        sim = qiskit_aer.AerSimulator()
        result = sim.run(qc, shots=1024).result()
        counts = result.get_counts()

        bitstring = max(counts, key=counts.get)
        reversed_bitstring = bitstring[::-1]
        return self.g_func[reversed_bitstring]


    def visualize_classical(self):
        """
        Visualization function that shows the graph comparison between theoretical 
        and actual runtime for the classical solution to this RFS problem.
        """

        ns = [2, 3, 4, 5, 6, 7]
        ls = [2, 3, 4, 5, 6, 7]
        actual_counts = []
        theoretical_counts = []
        labels = []

        for n in ns:
            for l in ls:

                call_count = 0
                self.solve_classically()
                actual_counts.append(call_count)
                theoretical_counts.append(n ** l)
                labels.append(f"{n}^{l}")


        data = list(zip(actual_counts, theoretical_counts, labels))

        data.sort(key=lambda tup: tup[0])

        actual_counts_sorted = [d[0] for d in data]
        theoretical_counts_sorted = [d[1] for d in data]
        labels_sorted = [d[2] for d in data]


        plt.plot(actual_counts, label="Real Runtime", marker='o')
        plt.plot(theoretical_counts, label="Theoretical Runtime (n^l)", linestyle='--', marker='x')
        plt.xticks(ticks=range(len(labels)), labels=labels, rotation=45)
        plt.xlabel("Input (n, l)")
        plt.ylabel("Runtime")
        plt.title("Real vs. Theoretical Runtime")
        plt.legend()
        plt.show()


    def visualize_quantum(self):
        """
        Visualization function that shows the quantum circuit used in the quantum solution.
        """
        qc = self.bernstein_vazirani_circuit()
        print(qc.draw())



# import matplotlib.pyplot as plt

# ns = [2, 3, 4, 5, 6, 7]
# ls = [2, 3, 4, 5, 6, 7]
# actual_counts = []
# theoretical_counts = []
# labels = []

# for n in ns:
#     for l in ls:
#         secrets = {

#         }
#         A_oracle = {

#         }
#         g_func = g_func_create(n)
#         g_secret_populate(n, l, secrets, g_func, A_oracle)

#         call_count = 0
#         c_rfs(())
#         actual_counts.append(call_count)
#         theoretical_counts.append(n ** l)
#         labels.append(f"{n}^{l}")



# # Step 1: Collect data points into tuples
# data = list(zip(actual_counts, theoretical_counts, labels))

# # Step 2: Sort by actual count (first item in each tuple)
# data.sort(key=lambda tup: tup[0])

# # Step 3: Unpack the sorted data back into separate lists
# actual_counts_sorted = [d[0] for d in data]
# theoretical_counts_sorted = [d[1] for d in data]
# labels_sorted = [d[2] for d in data]


# # Plotting
# plt.plot(actual_counts_sorted, label="Actual Call Count", marker='o')
# plt.plot(theoretical_counts_sorted, label="n^l (Theoretical)", linestyle='--', marker='x')
# plt.xticks(ticks=range(len(labels)), labels=labels, rotation=45)
# plt.xlabel("Input (n, l)")
# plt.ylabel("Function Calls")
# plt.title("Actual vs Theoretical Call Growth")
# plt.legend()
# # plt.tight_layout()
# plt.show()






# def create_rfs_problem(n, l, ):
