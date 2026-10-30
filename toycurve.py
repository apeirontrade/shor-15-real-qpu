"""A miniature twisted Edwards curve with the same equation as Ed25519 (Algorand's signature curve).

Ed25519:   -x^2 + y^2 = 1 + d*x^2*y^2   over p = 2^255 - 19   (p = 5 mod 8, d a non-square)
Toy curve: the same equation, same rules, over a tiny prime, so it fits on a 20-qubit chip.
"""


def is_square(v, p):
    return v % p == 0 or pow(v, (p - 1) // 2, p) == 1


class Curve:
    def __init__(self, p, d):
        assert p % 8 == 5 and not is_square(d, p), "keep Ed25519's choices: p = 5 mod 8, d non-square"
        self.p, self.d = p, d % p

    def on_curve(self, P):
        x, y = P
        p = self.p
        return (-x * x + y * y - 1 - self.d * x * x * y * y) % p == 0

    def add(self, P, Q):
        """Ed25519's (complete) twisted Edwards addition law with a = -1."""
        (x1, y1), (x2, y2), p, d = P, Q, self.p, self.d
        t = d * x1 * x2 * y1 * y2 % p
        x3 = (x1 * y2 + y1 * x2) * pow(1 + t, -1, p) % p
        y3 = (y1 * y2 + x1 * x2) * pow(1 - t, -1, p) % p
        return x3, y3

    def mul(self, k, P):
        R, Q = (0, 1), P  # (0, 1) is the identity
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q, k = self.add(Q, Q), k >> 1
        return R

    def order(self, P):
        n, R = 1, P
        while R != (0, 1):
            R, n = self.add(R, P), n + 1
        return n

    def points(self):
        return [(x, y) for x in range(self.p) for y in range(self.p) if self.on_curve((x, y))]


def find_toy(order=8):
    """Smallest Ed25519-style curve with a point of the requested order."""
    for p in range(13, 200):
        if p % 8 != 5 or any(p % q == 0 for q in range(2, int(p ** 0.5) + 1)):
            continue
        for d in range(2, p):
            if is_square(d, p):
                continue
            c = Curve(p, d)
            pts = c.points()
            for P in pts:
                if c.order(P) == order:
                    return c, P, len(pts)
    raise ValueError


if __name__ == "__main__":
    c, G, n = find_toy(8)
    print(f"toy curve: -x^2 + y^2 = 1 + {c.d} x^2 y^2  (mod {c.p}),  {n} points")
    print("generator G =", G, "order", c.order(G))
    for k in range(8):
        print(k, c.mul(k, G))
