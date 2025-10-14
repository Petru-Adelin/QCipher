import qiskit as qsk
from qiskit_aer import AerSimulator
import time



class Encoder:

    def __init__(self, key: bytes):
        if key:
            self.key = key
        else:
            self._set_key()
        time.sleep(2)
        print(self.key)

    def _xor_block_cipher(self, data, key):
        block_size = len(key)
        encrypted = bytearray()
        
        for i in range(0, len(data), block_size):
            block = data[i:i + block_size]
            encrypted_block = bytearray(b ^ k for b, k in zip(block, key))
            encrypted += encrypted_block
            
        return bytes(encrypted)

    # returns the IV (initialization vector) for the block cypher
    def _get_random_seed(self) -> int:
            
        circuit = qsk.QuantumCircuit(16, 16)

        for i in range(16):
            circuit.h(i)
        circuit.measure([*range(16)], [*range(16)])

        simulator = AerSimulator()
        transpiled_circ = qsk.transpile(circuit, simulator)
        results = simulator.run(transpiled_circ, shots=1).result()
        counts = results.get_counts()

        key = list(counts.keys())[0] 
        return int(key, 2)
    

    def _set_key(self):
        IV = self._get_random_seed()
        num_bytes = 2
        self.key = IV.to_bytes(num_bytes, byteorder='big')

    def encrypt(self, msg):
        global key
        cipher = self._xor_block_cipher(msg, self.key)
        return cipher 

    def decrypt(self, msg):
        global key
        cipher = self._xor_block_cipher(msg, self.key)
        return cipher 
    

if __name__ == "__main__":
    e = Encoder()
    text = b"Adelin Petru-Cojocaru"
    cypher = e.encrypt(text)
    print(cypher)
    print(e.decrypt(cypher))

    