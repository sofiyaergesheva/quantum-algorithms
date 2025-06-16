from matplotlib import pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
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
    plot_histogram(counts)
    plt.xlabel('Состояние')
    plt.ylabel('Частота измерения')
    plt.show()
    qc.draw(output="mpl")
    plt.show()
    most_probable = max(counts, key=counts.get)
    estimated_phi = int(most_probable, 2) / 2 ** n
    return estimated_phi


if __name__ == "__main__":
    true_phi = Fraction(3, 7)
    phi_float = float(true_phi)
    results = []
    for n in range(1, 8):
        estimated = run_qpe(true_phi, n)
        error = abs(phi_float - estimated)
        results.append((n, estimated, error))
    ns = [r[0] for r in results]
    estimates = [r[1] for r in results]
    errors = [r[2] for r in results]
    plt.figure(figsize=(10, 5))
    plt.plot(ns, errors, marker='o')
    plt.xlabel('Количество кубитов (n)')
    plt.ylabel('Погрешность')
    plt.grid(True)
    plt.show()
    print(f"Ожидаемая фаза: {float(true_phi):.6f}")
    print(f"Оценённая фаза: {run_qpe(true_phi, 8):.6f}")
