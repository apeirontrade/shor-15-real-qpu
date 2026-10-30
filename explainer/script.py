"""Narration for the long explainer, one entry per scene: (scene id, narration, on-screen caption).

Written as "we" so it works in a synthetic voice or Rob's own.
Every factual line is in ~/.claude/email-claims/2026-10-30-locks-x-post.md.
"""

SCRIPT = [
    ("cold_open",
     "We rented a real quantum computer for six dollars, and tried to break the locks that protect the internet. "
     "Some of them broke. One of them, we couldn't even attack. Here's what happened.",
     "We rented a real quantum computer for $6"),
    ("title", "", ""),
    ("bits",
     "A normal computer works with bits. Each one is a zero or a one, like a coin lying flat. "
     "A qubit is more like a coin that's still spinning. Until you look, it carries a bit of both.",
     "Bit: heads or tails.  Qubit: still spinning."),
    ("interference",
     "The real trick is interference. Like waves on a pond, wrong answers can cancel each other out, "
     "and the right answer can pile up. A quantum algorithm is a way of arranging those waves.",
     "Wrong answers cancel. Right answers pile up."),
    ("chip",
     "Our chip was IQM Garnet: twenty superconducting qubits, rented through Amazon Braket, by the shot. "
     "Chips like this run colder than outer space. Each shot cost us less than a cent.",
     "IQM Garnet · 20 qubits · Amazon Braket"),
    ("locks",
     "We picked four kinds of lock. R S A, which guards websites and banks. "
     "Elliptic curves, which guard Bitcoin, Ethereum, and Algorand. "
     "A E S and SHA two fifty six, which protect stored data and hashing. "
     "And Falcon, a new lock designed for the quantum age.",
     "4 kinds of lock"),
    ("rsa_idea",
     "Lock one: R S A. Multiplying two primes is easy. Splitting the answer back into its primes is brutally hard. "
     "That one-way street is the whole lock.",
     "Multiply: easy.  Un-multiply: hard."),
    ("rsa_clock",
     "Shor's algorithm cheats by looking for a rhythm. Take seven, and keep multiplying by seven on a fifteen-hour clock. "
     "One, seven, four, thirteen, and back to one. It repeats every four steps.",
     "7ˣ on a 15-hour clock: 1 → 7 → 4 → 13 → 1"),
    ("rsa_result",
     "The quantum chip found that rhythm through interference. Ninety two percent of its shots landed on the right answers. "
     "A little classic math on the rhythm of four gives three and five. Fifteen equals three times five.",
     "15 = 3 × 5"),
    ("vault",
     "Now, fifteen isn't exactly a bank vault. Real R S A uses numbers over six hundred digits long. "
     "Breaking it would take under a million qubits, by Google's latest estimate. We had twenty. "
     "That's testing a bank vault with a toothpick.",
     "RSA-2048: < 1,000,000 qubits.  Us: 20."),
    ("ecc_idea",
     "Lock two: elliptic curves. Picture hopping around a curve. Your secret key is the number of hops. "
     "Your public key is where you land. Going forward is easy. Working backward is the hard part.",
     "Secret = number of hops.  Public = where you land."),
    ("ecc_mini",
     "We built a mini copy of Algorand's curve. Same equation, but sixteen points instead of a seventy seven digit number. "
     "We gave the chip only the public key.",
     "Mini Ed25519 curve: 16 points"),
    ("ecc_result",
     "And it found the secret key. Key three, with three hundred eleven votes, against seventy eight for the runner up. "
     "To be fair, there were only four possible keys. You could do this one by hand.",
     "Secret key found: 3"),
    ("ecc_real",
     "The real curve is a different story. Google estimates under five hundred thousand physical qubits. Toothpick, meet vault.",
     "256-bit curves: < 500,000 qubits"),
    ("aes",
     "Lock three: A E S. There's no rhythm to find here, so the best quantum attack is Grover's search. "
     "It finds a needle in a haystack in about the square root of the number of tries. "
     "Our chip found a three bit key in two checks. Sixty nine percent of shots were right.",
     "Grover: found the key in 2 checks"),
    ("aes_real",
     "But a square root of a giant number is still giant. A E S two fifty six would still need a thirty nine digit number of steps. "
     "This lock holds.",
     "AES-256: still a 39-digit number of steps"),
    ("falcon",
     "Lock four: Falcon. We didn't attack it, because there's nothing to run. "
     "Falcon hides its secret in a lattice, a maze with hundreds of dimensions, and nobody has found a rhythm in it for Shor's trick to grab. "
     "No known quantum attack.",
     "Falcon: no known quantum attack"),
    ("limits",
     "Now, the honest part. Our locks were toys. Our circuits were hand built for each one. "
     "Between eight and thirty five percent of our shots were just noise. "
     "And winning at toy size proves nothing about real size, in either direction.",
     "Our limitations"),
    ("bigger",
     "Could we rent a bigger machine? Yes. Amazon has a one hundred and seven qubit chip online right now. "
     "But more noisy qubits isn't the answer. You need error correction: bundles of noisy qubits acting as one reliable qubit. "
     "The record is seventy of those. Breaking a real curve needs about twelve hundred.",
     "Error-corrected record: 70.  Needed: ~1,200."),
    ("score",
     "So here's the scoreboard. R S A and elliptic curves: breakable, once big quantum computers exist. "
     "A E S two fifty six, and Falcon: still standing.",
     "Scoreboard"),
    ("chains",
     "Our elliptic curve result isn't just about one coin. Bitcoin, Ethereum, Solana, Cardano, X R P, B N B Chain, Avalanche, "
     "Tron, Dogecoin, Litecoin, Polkadot, Stellar, and Algorand all sign transactions with elliptic curves. "
     "Their mining and hashing hold up. Their signatures don't.",
     "Major chains that sign with elliptic curves"),
    ("algorand",
     "And Algorand? Its standard accounts use an elliptic curve, the same kind of risk as Bitcoin and Ethereum. "
     "An Algorand address is its public key, so that starting point is always visible. "
     "But Algorand's main network already supports Falcon accounts. "
     "Bitcoin's main quantum proposal is still a draft.",
     "Where Algorand stands"),
    ("when",
     "So when does this get real? Experts surveyed in twenty twenty five put the odds at twenty eight to forty nine percent "
     "within ten years. The U S government wants its most important systems switched over by twenty thirty one.",
     "When?"),
    ("outro",
     "Not today. But the math works. Upgrade before Q Day. "
     "The code and every raw result are public. Link below.",
     "Not today. But the math works."),
]
