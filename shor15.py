"""Shor's algorithm for N=15, a=7 — the textbook hand-built circuit.

Honest framing: the modular-multiplication gates below are written knowing N=15
(same as every published small-number Shor demo). The quantum part finds the
period r of 7^x mod 15; the classical part turns r into the factors.

Qubits 0-2: counting register (phase estimation). Qubits 3-6: work register (holds 7^x mod 15).
"""
import json
import sys
from fractions import Fraction
from math import gcd, pi

from braket.circuits import Circuit

N, A = 15, 7
COUNT = [0, 1, 2]
WORK = [3, 4, 5, 6]  # WORK[0] = least-significant bit


def c_mult(circ, ctrl, power):
    """Controlled multiply-by-(7^power mod 15) on the work register, built from swaps + NOTs."""
    w = WORK
    m = pow(A, power, N)
    if m == 1:
        return  # 7^4 mod 15 = 1: identity, nothing to do
    if m == 7:
        circ.cswap(ctrl, w[2], w[3]).cswap(ctrl, w[1], w[2]).cswap(ctrl, w[0], w[1])
        for q in w:
            circ.cnot(ctrl, q)
    elif m == 4:
        circ.cswap(ctrl, w[1], w[3]).cswap(ctrl, w[0], w[2])
    else:
        raise ValueError(m)


def inverse_qft(circ, qubits):
    n = len(qubits)
    for i in range(n // 2):
        circ.swap(qubits[i], qubits[n - 1 - i])
    for j in range(n):
        for k in range(j):
            circ.cphaseshift(qubits[k], qubits[j], -pi / 2 ** (j - k))
        circ.h(qubits[j])


def build(light=False):
    """light=True uses the shortcut every hardware demo uses: the work register starts at 1,
    so the first controlled-multiply-by-7 only has to turn 0001 into 0111 (two CNOTs instead of
    three Fredkin gates). Fewer gates means less noise on a real chip."""
    circ = Circuit()
    circ.x(WORK[0])  # work register = 1
    for q in COUNT:
        circ.h(q)
    for j, q in enumerate(COUNT):
        if light and j == 0:
            circ.cnot(q, WORK[1]).cnot(q, WORK[2])  # 1 -> 7
        else:
            c_mult(circ, q, 2 ** j)
    inverse_qft(circ, COUNT)
    return circ


def counting_value(bitstring):
    """Braket bitstrings list qubit 0 first. Counting qubit j is bit j of the phase numerator."""
    return sum(int(bitstring[q]) << j for j, q in enumerate(COUNT))


def marginal(counts):
    out = {v: 0 for v in range(2 ** len(COUNT))}
    for bits, c in counts.items():
        out[counting_value(bits)] += c
    return out


def factors_from(value):
    """Classical post-processing: phase -> period r -> gcd(a^(r/2) +/- 1, N)."""
    phase = Fraction(value, 2 ** len(COUNT))
    r = phase.limit_denominator(N).denominator
    if r % 2 or pow(A, r, N) != 1:
        return r, None
    x = pow(A, r // 2, N)
    f = sorted({gcd(x - 1, N), gcd(x + 1, N)})
    return r, f if 1 not in f and N not in f else None


if __name__ == "__main__":
    from braket.devices import LocalSimulator

    light = "--light" in sys.argv
    sys.argv = [a for a in sys.argv if a != "--light"]
    circ = build(light)
    twoq = sum(1 for i in circ.instructions if len(i.target) + len(i.control) >= 2)
    print("instructions:", len(circ.instructions), "multi-qubit:", twoq, "depth:", circ.depth)
    shots = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    res = LocalSimulator().run(circ, shots=shots).result()
    m = marginal(res.measurement_counts)
    for v, c in m.items():
        print(f"{v:03b} ({v}/8)  {c:5d}  -> r, factors = {factors_from(v)}")
    json.dump({"device": "LocalSimulator", "light": light, "shots": shots, "marginal": m},
              open("results/sim_result_light.json" if light else "results/sim_result.json", "w"), indent=1)
