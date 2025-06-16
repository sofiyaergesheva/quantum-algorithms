import random
import numpy as np
from matplotlib import pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
import math


def grover_oracle(qc, threshold, values, f):
    num_values = len(values)
    num_qubits = int(np.ceil(np.log2(num_values)))
    for i in range(num_values):
        if f(values[i]) >= threshold:
            continue
        binary_index = format(i, f'0{num_qubits}b')
        for j, bit in enumerate(binary_index):
            if bit == '0':
                qc.x(j)
        qc.h(num_qubits - 1)
        qc.mcx(list(range(num_qubits - 1)), num_qubits - 1)
        qc.h(num_qubits - 1)
        for j, bit in enumerate(binary_index):
            if bit == '0':
                qc.x(j)


def diffusion_operator(qc, values):
    num_qubits = int(np.ceil(np.log2(len(values))))
    qc.h(range(num_qubits))
    qc.x(range(num_qubits))
    qc.h(num_qubits - 1)
    qc.mcx(list(range(num_qubits - 1)), num_qubits - 1)
    qc.h(num_qubits - 1)
    qc.x(range(num_qubits))
    qc.h(range(num_qubits))


def durr_hoyer(values, f):
    num_values = len(values)
    num_qubits = int(np.ceil(np.log2(num_values)))
    max_iterations = int(22.5 * math.sqrt(num_values) + 1.4 * (math.log2(num_values) ** 2))
    iterations = 1
    x0 = random.choice(values)
    y0 = f(x0)
    print(f"Начальный x0: {x0}, f(x0) = {y0}")
    final_qc = None
    while iterations <= max_iterations:
        qc = QuantumCircuit(num_qubits)
        qc.h(range(num_qubits))
        qc.barrier()
        for _ in range(int((math.pi/4)*math.sqrt(num_values))):
            grover_oracle(qc, y0, values, f)
            qc.barrier()
            diffusion_operator(qc, values)
            qc.barrier()
        qc.barrier()
        qc.measure_all()
        if iterations == max_iterations:
            final_qc = qc
        simulator = AerSimulator()
        compiled = transpile(qc, simulator)
        result = simulator.run(compiled, shots=1000).result()
        counts = result.get_counts()
        measured = max(counts, key=counts.get)
        index = int(measured, 2)
        if index >= len(values):
            iterations += 1
            continue
        x = values[index]
        y = f(x)
        if y < y0:
            x0, y0 = x, y
        iterations += 1
    if final_qc:
        simulator = AerSimulator()
        compiled = transpile(final_qc, simulator)
        result = simulator.run(compiled, shots=1000).result()
        counts = result.get_counts()
        plot_histogram(counts)
        plt.xlabel('Состояние')
        plt.ylabel('Частота измерения')
        plt.show()
        final_qc.draw(output="mpl")
        plt.show()
    print(f"Результат: x = {x0}, f(x) = {y0}\n")
    return x0


def find_min(list, func, min):
    for i in range(int(math.log2(len(list)))):
        print(f"Итерация {i}:")
        durr_hoyer_min = durr_hoyer(list, func)
        if durr_hoyer_min < min:
            min = durr_hoyer_min
    return min


if __name__ == "__main__":
    values = [10, 7, 58, 23, 48, 1, 12, 27, 9, 62, 46, 50, 39, 5, 47, 54]
    f = lambda x: x ** 2
    min_val = 10 ** 9
    minimum = find_min(values, f, min_val)
    print(f"Минимум равен: {minimum}")
