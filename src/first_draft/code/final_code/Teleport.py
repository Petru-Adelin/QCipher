import qiskit as qsk
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit
from own_types import *
import numpy as np



class Teleport:
    def __init__(self, no_bits: int):
        self.a_bits = np.random.randint(0, 2, size=no_bits)
        self.circuits: Circs = []

    def __initCircuits(self) -> None:
        for bit in self.a_bits:
            circuit = QuantumCircuit(3, 3)
            # transform the bit to |1>
            if bit == 1:
                circuit.x(0)
            
            circuit.barrier()
            # prepare the bell state 
            circuit.h(1)
            circuit.cx(1, 2)
            circuit.barrier()

            # execute the teleportation 
            circuit.cx(0, 1)
            circuit.h(0)
            # measure the first two qbits 
            circuit.measure(0, 0)
            circuit.measure(1, 1)
            # apply CTRX and CTRZ based on the results in the measurement
            circuit.cx(1, 2)
            circuit.cz(0, 2)
            circuit.barrier()
            # mesure the result 
            circuit.measure(2, 2)
            self.circuits.append(circuit)


    # public method
    def run(self):
        # init the circuits
        self.__initCircuits()
        simulator = AerSimulator()
        results = []
        for circuit in self.circuits:
            transp = qsk.transpile(circuit, simulator)
            job = simulator.run(transp, shots=1)
            result = job.result()
            counts = result.get_counts()
            key = list(counts.keys())[0]
            # we are interested in the last bit from each key - which is a string
            # last bit in the qiskit order is the left most also key[0]
            results.append(int(key[0]))
        return results 
    
    def plot_circuit(self, idx: int):
        return self.circuits[idx].draw('mpl')

    

