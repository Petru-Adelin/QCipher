import numpy as np
import matplotlib.pyplot as plt 
import qiskit as qsk 
from qiskit_aer import AerSimulator
import copy
from collections import deque
from own_types import *

# BB84 class is a util class created to store all the methods needed for the Protocol
# The class should 
# 
# 
class Upper_Block:
        i: int = 0

        def __init__(self, indeces: Bits, iter: int):
            self.id = f'BLK_{Upper_Block.__i}'
            Upper_Block.__i += 1
            self.indeces = indeces
            self.iter = iter 
            self.parity = -1

        @classmethod
        def reset(cls):
            cls.__i = 0
        
        def __str__(self) -> str:
            return f'Block: {self.id} | Indeces: {self.indeces} | Iter: {self.iter} | Parity: {self.parity}'



class BB84: 
    
    def __init__(self, no_bits: int, *, picking_rate: float = .7, compare_rate: float = .33):
        self.a_bits: Bits = np.random.randint(0, 2, size=no_bits)
        self.a_bases: Bases = np.random.randint(0, 2, size=no_bits)
        self.b_bases: Bits = np.random.randint(0, 2, size=no_bits)
        self.b_bits: Bits = []
        self.key_idx: Idxs = []
        self.for_comp_idx: Idxs = []
        self.circuits: Circs = []
        self.eavesdropping: list[tuple[Iter, Bit, Base]] = []
        self.PICKING_RATE = picking_rate
        self.QBER = 0.0
        self.COMPARE_RATE = compare_rate

    def __str__(self):
        return f'################### BB84 ###################\n Bits sent: {self.a_bits}\n Bases for encryption: {self.a_bases}\n\
###########################################\n Bases for decryption: {self.b_bases} \n\
###########################################\nPICKING RATE: {self.PICKING_RATE}\nEaves Results (Iter, Bit, Base): {self.eavesdropping}\n\
###########################################\n KEY_IDX: {self.key_idx}\n\
###########################################\nQBER: {self.QBER}\n\
###########################################'

    def __encodingPersending(self) -> None:
        if len(self.circuits) != 0:
            self.circuits.clear()

        if len(self.a_bases) != len(self.a_bits):
            raise Exception("####### Error in the encode_persending function <:> Length of the bases list should be equal to the length of bits list")

        for base, bit in zip(self.a_bases, self.a_bits):
            circ = QuantumCircuit(1, 1)
            # Z-base (vertical - |0> & |1>)
            if base == 0:
                # Apply a PauliX Gate on the qbit
                if bit == 1:
                    circ.x(0)
            # X-base (horizontal - |+> & |->)
            else:
                if bit == 1:
                    circ.x(0)
                circ.h(0)
            # Add the circuit to the list of circuits to be run after by the simulator
            self.circuits.append(circ)

    # For the measurement we simple choose a seq of random bases and whenever the base |+> & |-> we apply a hadamard gate to invert the 
    # qbit in the normal Z-base for |0> & |1> we leave the qbits as they are 
    def __measurements(self) -> None:
        if len(self.circuits) != len(self.b_bases):
            raise Exception("####### Error in the measure function <:> Length of the bases list should be equal to the length of circuits list")

        for circ, base in zip(self.circuits, self.b_bases):
            if base == 1:
                circ.h(0)
            circ.measure(0, 0)


    def __eavesdropping(self) -> list[tuple[Iter, Bit, Base]]:
        size = len(self.circuits)
        eve_choice = np.random.choice([True, False], p=[self.PICKING_RATE, 1-self.PICKING_RATE], size=size)

        # measure, write down and resend the qbit
        results: list[tuple[Iter, Bit, Base]] = []
        for i, circuit in enumerate(self.circuits):
            # deciding eihter to measure or not
            if eve_choice[i]:
                # choose a bases for measurement at random
                base = np.random.randint(0, 2)
                if base == 1:
                    circuit.h(0)
                circuit.measure(0, 0)

                # Simulate the circuit and get the result 
                simulator = AerSimulator()
                trans = qsk.transpile(circuit, simulator)
                job = simulator.run(trans, shots=1)
                res = job.result().get_counts()
                value = int(list(res.keys())[0])
                results.append((i, value, base))
                # re-prepering the qbit 
                circuit_new = QuantumCircuit(1, 1)
                if base == 0:
                    if value == 1:
                        circuit_new.x(0)
                else:
                    if value == 1:
                        circuit_new.x(0)
                    circuit_new.h(0)

                # replace the old circuite with the new one 
                circuit = circuit_new 

        return results

    def __filter_out(self) -> Idxs:
        indeces = []
        for i, bases in enumerate(zip(self.a_bases, self.b_bases)):
            if bases[0] == bases[1]:
                indeces.append(i)
        return indeces
    
    # public methods
    # de implementat mai pe seara cand ajung acasa
    def run(self) -> Bits:
        self.__encodingPersending()
        self.eavesdropping = self.__eavesdropping()
        self.__measurements()
        # simulating the circuits
        sim = AerSimulator()
        
        for circuit in self.circuits:
            trans = qsk.transpile(circuit, sim)
            job = sim.run(trans, shots=1)
            counts = job.result().get_counts()
            self.b_bits.append(int(list(counts.keys())[0]))

        print(f'Bobs after quantum circs: {self.b_bits}')
        # filter the indeces of the matching bits
        self.key_idx = self.__filter_out()
        print(f'The Key idx: {self.key_idx}')

        # compute the QBER error
        # compare just some of the bits (randomly chosen from the list of indeces)
        how_many = int(self.COMPARE_RATE * len(self.key_idx))
        self.for_comp_idx = np.random.choice(self.key_idx, size=how_many)

        print(f'for_comparison: {self.for_comp_idx}')
        # update the key 

        print(f'Bobs: {self.b_bits}')
        wrong_bits = 0
        for i in self.for_comp_idx:
            if self.b_bits[i] != self.a_bits[i]:
                wrong_bits += 1
        
        self.QBER = wrong_bits / len(self.key_idx)
        # we update the key after the computation of the QBER
        self.key_idx = [k for k in self.key_idx if k not in self.for_comp_idx]
        print(f'Updated key: {self.key_idx}')
        return [self.b_bits[i] for i in self.key_idx]



class CascadeReconcill:

    
    def __init__(self, protocol: BB84):
        self.key_bits = protocol.run()
        self.key_idxs = protocol.key_idx
        self.protocol = protocol
        self.blocks: list[Upper_Block] = []
        Upper_Block.reset()
    
    def __inv_bit(self, b: Bit) -> Bit:
        return 0 if b == 1 else 1


    def __binarySplit(self, indeces: Idxs) -> int:
        if len(indeces) == 1:
            return indeces[0]
        # recursive break the bit_block into two parts and select the one who presents an odd-error
        break_point = len(indeces) // 2
        left_parity = self.__getParity(indeces[:break_point])
        if left_parity % 2 == 1:
            return self.__binarySplit(indeces[:break_point])
        else: 
            return self.__binarySplit(indeces[break_point:])
        
    def __blockGen(self, k: int, ite: int, first_ite_flag: bool = True) -> list[Upper_Block]:
        indeces = self.key_idxs
        print(f'indeces: {indeces}')
        step = 0 
        blocks: list[Upper_Block] = []
        while step + k < len(indeces):
            if not first_ite_flag:
                # shuffle the indeces 
                np.random.shuffle(indeces)
            # break down the indeces' list
            # and set the iteration it was made in
            block = Upper_Block(indeces[step:step+k], ite)
            # set the true parity
            block.parity = self.__getParity(block.indeces)
            blocks.append(block)

            # proceed with iteration
            step += k 
        
        # last check for a Upper Block of fewer bits
        if step < len(indeces):
            block = Upper_Block(indeces[step:], ite)
            block.parity = self.__getParity(block.indeces)
            blocks.append(block)
        return blocks
    
    def __cascade(self, q: dict[int, list[Upper_Block]], iter: int):
        keys = list(q.keys())
        keys.reverse()
        keys = [k for k in keys if k < iter]
        print(f'Keys in the cascade for iter {iter} are: {keys}')
        for key in keys:
            blocks = q[key]
            # traverse the blocks 
            for block in blocks:
                block.parity = self.__getParity(block.indeces)
                print(f'TRAVERSED BLOCK: {block}')
                if block.parity % 2 == 1:
                    # get 
                    idx = self.__binarySplit(block.indeces)
                    self.protocol.b_bits[idx] = self.inv_bit(self.protocol.b_bits[idx])
                    block.parity = self.getParity(block.indeces)
                    print(f'UPDATED BLOCK: {block}')


    def __getParity(self, indeces: Idxs) -> int:
        count = 0
        for i in indeces:
            if self.protocol.a_bits[i] != self.protocol.b_bits[i]:
                count += 1
        return count 

    # public method
    def reconcill(self) -> Bits:
        if self.protocol.QBER == 0.0:
            k = 4
        else:
            k = int(.73 / self.protocol.QBER)

        # k = k if k != 0 else 2
        print(f'\n\n\n########################################')
        print(f'K value: {k}')
        it = 1
        q: dict[int, list[Upper_Block]] = {}
        while k < len(self.protocol.key_idx):  
            blocks = self.__blockGen(k, it, it == 1)
            self.blocks = [*self.blocks, *blocks]
            k *= 2
            it += 1

        for _ in self.blocks:
            print(_)
        for block in self.blocks:
            # update parity
            block.parity = self.__getParity(block.indeces)
            # add it to the history of checked blocks
            if block.iter in q.keys():
                q[block.iter].append(block)
            else:
                q[block.iter] = [block]
            # check if the parity is odd 
            if block.parity % 2 == 1:
                idx = self.__binarySplit(block.indeces)
                self.protocol.b_bits[idx] = self.__inv_bit(self.protocol.b_bits[idx])
                block.parity = self.__getParity(block.indeces)
                self.__cascade(q, block.iter)
        # Update the key and return it to the user
        self.key_bits = [self.protocol.b_bits[i] for i in self.key_idxs]
        return self.key_bits
        