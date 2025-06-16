from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import QFT
from numpy import pi
from fractions import Fraction


def run_qpe(phi: Fraction, n):
    m = 1
    qc = QuantumCircuit(n + m, n)
    qc.x(n)
    qc.h(range(n))
    for j in range(n):
        angle = 2 * pi * float(phi) * (2 ** j)
        qc.cp(angle, j, n)
    qc.append(QFT(n, inverse=True, do_swaps=True).to_gate(label="QFT†"), range(n))
    qc.measure(range(n), range(n))
    simulator = AerSimulator()
    compiled = transpile(qc, simulator)
    result = simulator.run(compiled, shots=1000).result()
    counts = result.get_counts()
    most_probable = max(counts, key=counts.get)
    estimated_phi = int(most_probable, 2) / 2 ** n
    return estimated_phi


if __name__ == "__main__":
    phi = Fraction(7, 9)
    print(f"Ожидаемая фаза: {float(phi):.6f}")
    print(f"Оценённая фаза: {run_qpe(phi, 8):.6f}")
