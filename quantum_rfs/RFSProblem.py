
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import random
import itertools
import qiskit_aer
#import matplotlib.pyplot as plt

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



    def apply_U_f(self, qc, n, f_table):
        """
        Implements U_f where f_table is a dict mapping bitstrings to {0,1}
        input_qubits: list of qubit indices for input
        output_qubit: index of output qubit
        """
        input_qubits = list(range(n))
        output_qubit = n

        
        for bitstring, fx in f_table.items():
            if fx == 1:
                # Invert bits where bitstring has 0
                for i, bit in enumerate(bitstring):
                    if bit == '0':
                        qc.x(input_qubits[i])
                
                # Apply MCX (multi-controlled X) gate
                qc.mcx(input_qubits, output_qubit)  # assumes enough ancillas for >4 controls
                
                # Undo inversion
                for i, bit in enumerate(bitstring):
                    if bit == '0':
                        qc.x(input_qubits[i])
            


    def bernstein_vazirani_circuit(self, qc, A, G, k, quantum_registers, ancilla_register):
        """
        This is the quantum circuit implementation of the Bernstein Vazirani solution to the RFS problem.

        Parameters
        -------
        qc  : QuantumCircuit
            Secret used to construct and check the solution
        s  : string
            Secret used to construct and check the solution

        Returns
        -------
        qc  : QuantumCircuit
            The quantum circuit of the Bernstein Vazirani solution to the problem.
        """

        if k == self.l:
            all_qubits = []
            for reg in quantum_registers:
                for qubit in reg:
                    all_qubits.append(qubit)
            all_qubits = all_qubits + [ancilla_register[0]]
            qc.append(A, all_qubits)
            return


        q_reg = QuantumRegister(self.n)
        qc.add_register(q_reg)
        for qubit in q_reg:
            qc.h(qubit)
        

        a_reg = QuantumRegister(1)
        qc.add_register(a_reg)
        qc.x(a_reg[0])
        qc.h(a_reg[0])

        self.bernstein_vazirani_circuit(qc, A, G, k+1, quantum_registers+(q_reg,), a_reg)

        recent_qreg_qubits = []
        for qubit in q_reg:
            qc.h(qubit)
            recent_qreg_qubits.append(qubit)
        
        g_input_qubits = recent_qreg_qubits + [ancilla_register[0]]
        qc.append(G, g_input_qubits)

        for qubit in q_reg:
            qc.h(qubit)

        self.bernstein_vazirani_circuit(qc, A, G, k+1, quantum_registers+(q_reg,), a_reg)
        
        return
    


    def solve_quantumly(self):
        """
        Overarching method that calls the recursion for the quantum solution.

        Returns
        -------
        g_secret  : number
            The g(secret) of the  root node (current node when recursive)
        """

        A_table = {''.join(k): int(v) for k, v in (self.A_oracle).items()}
        print(A_table)

        q_reg = QuantumRegister(1)
        c_reg = ClassicalRegister(1, name='c')
        qc = QuantumCircuit(q_reg, c_reg)


        A = QuantumCircuit(self.n * self.l + 1, name= '      A      ')
        A_table = {''.join(k): int(v) for k, v in (self.A_oracle).items()}
        self.apply_U_f(A, self.n * self.l, f_table=A_table)

        # print(A.draw())

        G = QuantumCircuit(self.n + 1, name='      G      ') 
        self.apply_U_f(G, self.n, f_table=self.g_func)

        self.bernstein_vazirani_circuit(qc, A, G, 0, (), q_reg)

        qc.measure(0, 0)


        # print(qc.draw(fold=1000))
        # qc.draw(output='mpl').savefig("pic.png")

        qc = qc.decompose()
        #print(qc.draw(fold=1000))

        sim = qiskit_aer.AerSimulator()
        result = sim.run(qc, shots=1024).result()
        counts = result.get_counts()
        print(counts)


        return self.g_func[self.secrets[()]]