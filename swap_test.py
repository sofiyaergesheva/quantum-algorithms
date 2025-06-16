import numpy as np
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def prepare_qubit_state(qc, qubit, theta, phi):
    qc.u(theta, phi, 0, qubit)


def prepare_registers(theta_a_list, phi_a_list, theta_b_list, phi_b_list):
    n = len(theta_a_list)
    assert len(phi_a_list) == n and len(theta_b_list) == n and len(phi_b_list) == n, "Длины параметров должны совпадать"
    ctrl = QuantumRegister(1)
    reg_a = QuantumRegister(n)
    reg_b = QuantumRegister(n)
    creg = ClassicalRegister(1)
    qc = QuantumCircuit(ctrl, reg_a, reg_b, creg)
    for i in range(n):
        prepare_qubit_state(qc, reg_a[i], theta_a_list[i], phi_a_list[i])
        prepare_qubit_state(qc, reg_b[i], theta_b_list[i], phi_b_list[i])
    return qc, ctrl, reg_a, reg_b, creg


def swap_test(qc, ctrl, reg_a, reg_b, creg):
    n = len(reg_a)
    qc.h(ctrl[0])
    for i in range(n):
        qc.cswap(ctrl[0], reg_a[i], reg_b[i])
    qc.h(ctrl[0])
    qc.measure(ctrl[0], creg[0])
    simulator = AerSimulator()
    compiled = transpile(qc, simulator)
    result = simulator.run(compiled, shots=1000).result()
    counts = result.get_counts()
    p1 = counts.get('1', 0) / 1000
    p0 = max(0.5, 1 - p1)
    s = max(0.0, 1 - 2 * p1)
    return p0, s


if __name__ == "__main__":
    theta_a = [np.pi / 2, 0]
    phi_a = [0, 0]
    theta_b = [np.pi / 2, 0]
    phi_b = [0, 0]
    qc, ctrl, reg_a, reg_b, creg = prepare_registers(theta_a, phi_a, theta_b, phi_b)
    p0, s = swap_test(qc, ctrl, reg_a, reg_b, creg)
    print(f"|⟨a|b⟩|² = {s:.4f}")
    print(f"P(0) = {p0:.4f}")
