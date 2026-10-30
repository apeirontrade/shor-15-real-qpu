"""Grover's search for a 3-bit key: the quantum attack on symmetric crypto (AES) and hashes (SHA-256).

Honest framing: the "lock" here is hard-wired to recognise key 101. In a real attack the check would be
the full AES circuit run on a superposition of keys, which needs thousands of error-corrected qubits.
Grover's speed-up is only a square root: 8 keys take ~2 quantum checks instead of ~4 classical guesses,
and AES-256's 2^256 keys still take ~2^128 steps.
"""
import json
from math import floor, pi, sqrt

from braket.circuits import Circuit

N_BITS = 3
SECRET = 0b101
ITERATIONS = floor(pi / 4 * sqrt(2 ** N_BITS))  # 2 for 8 keys


def ccz(circ, a, b, t):
    circ.h(t).ccnot(a, b, t).h(t)


def oracle(circ):
    """Flip the sign of the secret key only."""
    flips = [q for q in range(N_BITS) if not (SECRET >> q) & 1]
    for q in flips:
        circ.x(q)
    ccz(circ, 0, 1, 2)
    for q in flips:
        circ.x(q)


def diffuser(circ):
    for q in range(N_BITS):
        circ.h(q).x(q)
    ccz(circ, 0, 1, 2)
    for q in range(N_BITS):
        circ.x(q).h(q)


def build():
    circ = Circuit()
    for q in range(N_BITS):
        circ.h(q)
    for _ in range(ITERATIONS):
        oracle(circ)
        diffuser(circ)
    return circ


def key_counts(counts):
    out = {k: 0 for k in range(2 ** N_BITS)}
    for bits, c in counts.items():
        out[sum(int(bits[q]) << q for q in range(N_BITS))] += c
    return out


if __name__ == "__main__":
    from braket.devices import LocalSimulator

    circ = build()
    print("iterations:", ITERATIONS, "instructions:", len(circ.instructions), "depth:", circ.depth)
    kc = key_counts(LocalSimulator().run(circ, shots=1000).result().measurement_counts)
    print({f"{k:03b}": c for k, c in kc.items()})
    json.dump({"device": "LocalSimulator", "shots": 1000, "keys": kc}, open("results/grover_sim.json", "w"), indent=1)
