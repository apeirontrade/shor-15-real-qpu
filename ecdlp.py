"""Shor's attack on elliptic-curve keys, run against a miniature Ed25519-style curve.

The attacker knows only public information: the curve, the base point G and the public key Q = k*G.
It wants the private key k.

The oracle |a>|b>|O> -> |a>|b>|a*G + b*Q> is built from public data only:
  - curve points are labelled by their sorted coordinates (no discrete logs used),
  - "add the public point C" is a permutation of those labels, worked out with the curve's addition law,
  - each permutation is turned into gates (CNOT / Toffoli / Fredkin), controlled by one counting qubit.
After an inverse QFT on both counting registers, every outcome (u, v) satisfies v = k*u (mod n),
so any shot with odd u reveals k = v * u^-1 (mod n).
"""
import itertools
import json
import sys
from collections import Counter

from braket.circuits import Circuit

from shor15 import inverse_qft
from toycurve import find_toy


def setup(order, k):
    curve, G8, _ = find_toy(8)
    G = curve.mul(8 // order, G8)  # generator of the order-n subgroup
    Q = curve.mul(k, G)  # public key
    subgroup = sorted(curve.mul(m, G) for m in range(order))  # sorted by coordinates: labels carry no logs
    label = {P: i for i, P in enumerate(subgroup)}
    return curve, G, Q, subgroup, label


def add_perm(curve, subgroup, label, C):
    return [label[curve.add(P, C)] for P in subgroup]


# ---------------------------------------------------------------- permutation -> gates
def _apply(ops, x, n):
    bits = [(x >> i) & 1 for i in range(n)]
    for op in ops:
        if op[0] == "swap":
            i, j = op[1:]
            bits[i], bits[j] = bits[j], bits[i]
        elif op[0] == "xor":  # bits[t] ^= bits[s]
            t, s = op[1:]
            bits[t] ^= bits[s]
        elif op[0] == "not":
            bits[op[1]] ^= 1
    return sum(b << i for i, b in enumerate(bits))


def synth(perm, n):
    """Shortest sequence of swaps / XORs / NOTs implementing perm (exists when perm is affine over GF(2))."""
    elem = [("swap", i, j) for i, j in itertools.combinations(range(n), 2)]
    elem += [("xor", t, s) for t in range(n) for s in range(n) if t != s]
    target = tuple(perm)
    for nots in itertools.chain.from_iterable(itertools.combinations(range(n), r) for r in range(n + 1)):
        tail = [("not", i) for i in nots]
        frontier = {tuple(range(2 ** n)): []}
        seen = set(frontier)
        for _ in range(8):
            for key, ops in list(frontier.items()):
                if tuple(_apply(ops + tail, x, n) for x in range(2 ** n)) == target:
                    return ops + tail
            nxt = {}
            for key, ops in frontier.items():
                for e in elem:
                    o = ops + [e]
                    k2 = tuple(_apply(o, x, n) for x in range(2 ** n))
                    if k2 not in seen:
                        seen.add(k2)
                        nxt[k2] = o
            frontier = nxt
    return None


def controlled(circ, ctrl, ops, work):
    for op in ops:
        if op[0] == "swap":
            circ.cswap(ctrl, work[op[1]], work[op[2]])
        elif op[0] == "xor":
            circ.ccnot(ctrl, work[op[2]], work[op[1]])
        else:
            circ.cnot(ctrl, work[op[1]])


def build(order, k):
    nb = order.bit_length() - 1
    A = list(range(nb))
    B = list(range(nb, 2 * nb))
    Wk = list(range(2 * nb, 3 * nb))
    curve, G, Q, subgroup, label = setup(order, k)
    circ = Circuit()
    o = label[(0, 1)]  # work register starts at the identity point
    for i in range(nb):
        if (o >> i) & 1:
            circ.x(Wk[i])
    for q in A + B:
        circ.h(q)
    for reg, base in ((A, G), (B, Q)):
        for j, q in enumerate(reg):
            ops = synth(add_perm(curve, subgroup, label, curve.mul(2 ** j, base)), nb)
            if ops is None:
                raise ValueError("permutation not affine; needs a generic synthesis")
            controlled(circ, q, ops, Wk)
    inverse_qft(circ, A)
    inverse_qft(circ, B)
    return circ, (A, B), (curve, G, Q)


def reg_value(bits, reg):
    return sum(int(bits[q]) << j for j, q in enumerate(reg))


def recover(counts, regs, order):
    """Every shot with odd u votes for k = v / u (mod n). Returns the vote tally and the 'valid' fraction."""
    A, B = regs
    votes, total = Counter(), sum(counts.values())
    pairs = Counter()
    for bits, c in counts.items():
        u, v = reg_value(bits, A), reg_value(bits, B)
        pairs[(u, v)] += c
        if u % 2:
            votes[v * pow(u, -1, order) % order] += c
    return votes, pairs, total


if __name__ == "__main__":
    from braket.devices import LocalSimulator

    order = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    circ, regs, (curve, G, Q) = build(order, k)
    print(f"curve -x^2+y^2 = 1+{curve.d}x^2y^2 mod {curve.p};  G={G}  public key Q={Q}  (secret k={k})")
    multi = sum(1 for i in circ.instructions if len(i.target) + len(i.control) >= 2)
    print("qubits:", circ.qubit_count, "instructions:", len(circ.instructions), "multi-qubit:", multi, "depth:", circ.depth)
    res = LocalSimulator().run(circ, shots=1000).result()
    votes, pairs, total = recover(res.measurement_counts, regs, order)
    valid = sum(c for (u, v), c in pairs.items() if (v - k * u) % order == 0)
    print("votes for k:", dict(votes), " valid (v = k*u) fraction:", valid / total)
    json.dump({"device": "LocalSimulator", "order": order, "curve": [curve.p, curve.d], "G": G, "Q": Q,
               "shots": total, "pairs": {f"{u},{v}": c for (u, v), c in sorted(pairs.items())},
               "votes": dict(votes)}, open(f"results/ecdlp_sim_order{order}.json", "w"), indent=1)
