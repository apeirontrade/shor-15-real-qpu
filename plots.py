"""Charts for the README, from the saved hardware and simulator results."""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ecdlp import build as ecdlp_build, recover
from grover import key_counts


def style(ax, title):
    ax.set_title(title, fontsize=11)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


light = json.load(open("results/qpu_result_light.json"))
full = json.load(open("results/qpu_result_full.json"))
ec = json.load(open("results/ecdlp_qpu.json"))
gr = json.load(open("results/grover_qpu.json"))

fig, axes = plt.subplots(1, 3, figsize=(15, 4.2), dpi=150)

ax = axes[0]
x = range(8)
for off, r, lab, col in ((-0.2, light, "light circuit, 450 shots", "#0ea5e9"), (0.2, full, "full circuit, 1000 shots", "#f472b6")):
    tot = sum(r["marginal"].values())
    ax.bar([i + off for i in x], [r["marginal"][str(v)] / tot for v in x], 0.4, label=lab, color=col)
ax.set_xticks(list(x), [f"{v:03b}" for v in x])
ax.set_ylabel("fraction of shots")
ax.legend(frameon=False, fontsize=8)
style(ax, "RSA toy: Shor, N=15 (ideal peaks 000/010/100/110)")

ax = axes[1]
votes, _, _ = recover(ec["raw_counts"], ecdlp_build(4, 3)[1], 4)
ax.bar(range(4), [votes.get(k, 0) for k in range(4)], color=["#64748b"] * 3 + ["#fbbf24"])
ax.set_xticks(range(4), [f"k={k}" for k in range(4)])
ax.set_ylabel("votes (shots with odd u)")
style(ax, "Elliptic-curve toy: recovered key (true k=3)")

ax = axes[2]
kc = key_counts(gr["raw_counts"])
ax.bar(range(8), [kc[k] for k in range(8)], color=["#fbbf24" if k == 5 else "#64748b" for k in range(8)])
ax.set_xticks(range(8), [f"{k:03b}" for k in range(8)])
ax.set_ylabel("shots")
style(ax, "AES toy: Grover, 3-bit key (true key 101)")

fig.suptitle("IQM Garnet (20-qubit superconducting) via Amazon Braket, 2026-10-30", fontsize=12)
fig.tight_layout()
fig.savefig("results/hardware_results.png")
print("results/hardware_results.png")
