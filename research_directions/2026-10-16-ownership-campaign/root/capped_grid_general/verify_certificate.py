"""Independent exact replay: no optimizer, builder import, or disabled asserts."""
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import json


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def taylor_negative(x, degree):
    require(x >= 0, "Taylor argument must be nonnegative")
    return sum(((-x) ** k / factorial(k) for k in range(degree + 1)), F(0))


PB, CB, DB = F(51, 40), F(148, 125), F(23, 125)
EL = sum((F(1, factorial(k)) for k in range(9)), F(0))
EU = EL + F(1, factorial(9)) * F(10, 9)
CL, CU = 1 + 1 / (2 * EU), 1 + 1 / (2 * EL)
KU = EU - 1


def replay():
    source = Path(__file__).with_name("certificate.json")
    proof = json.loads(source.read_text())
    require(proof["target"] == "13/8" and F(proof["PB"]) == PB, "target/header")
    require(CU < CB and CU - 1 < DB and KU ** 2 < 3, "constant enclosures")
    # exp(-C) >= Taylor_25(-CU); then the outer exponential decreases.
    inner_lower = taylor_negative(CU, 25)
    require(inner_lower > 0, "positive inner exponential lower bound")
    high_grid_upper = 1 + taylor_negative(PB - 1, 24) * (
        PB + taylor_negative(inner_lower, 24) / 2
    ) / 2
    require(high_grid_upper < F(13, 8), "high capped-grid regime")
    require(CU ** 2 < F(13, 8), "physical power bottleneck")
    # L(3/4)=4/(3sqrt(e))>4/5 follows from e<25/9.
    require(EU < F(25, 9), "negative-gap saving constant")
    require(proof["S_intervals"] == 128 and proof["delta_intervals"] == 8,
            "grid dimensions")
    cells = proof["cells"]
    require(len(cells) == 128 * 8, "all continuous rectangles included")
    bounds, empty = [], 0
    for index, cell in enumerate(cells):
        si, di = divmod(index, 8)
        lo = 1 + (PB + CB - 1) * si / 128
        hi = 1 + (PB + CB - 1) * (si + 1) / 128
        dl, dh = DB * di / 8, DB * (di + 1) / 8
        for key, expected in (("s_lo", lo), ("s_hi", hi), ("d_lo", dl), ("d_hi", dh)):
            require(F(cell[key]) == expected, f"rectangle {index}: {key}")
        if "empty_reason" in cell:
            require(lo > PB + CU - dl, f"rectangle {index}: empty certificate")
            require("upper" not in cell, "empty rectangle has conflicting data")
            empty += 1
            continue
        u = F(cell["u"])
        require(0 < u < 1, "valid supporting parameter")
        ql = taylor_negative(1 / u - 1, 25) / 2
        qh = taylor_negative(1 / u - 1, 24) / 2
        al, ah = 1 - qh * (1 + 1 / u), 1 - ql * (1 + 1 / u)
        require(0 < ql <= qh and 0 < al <= ah, "positive coefficient bounds")
        lam = 1 - ql * (1 + 1 / u - 1 / lo)
        eta = qh / lo
        mu = KU ** 2 * eta ** 2 / (4 * al)
        p = KU * eta
        saving = F(2, 5) * taylor_negative(hi - 1 + dh, 25)
        require(lam > 0 and saving > 0, "positive support/saving bounds")
        matrix = [
            [1, -1, 0, 0, 0], [-CU, 1, 0, 0, 0], [0, -1, 0, 0, 0],
            [-1, 1, 1, 0, 0], [0, 1, 1, 0, 0], [0, 0, 1, 1, 0],
            [F(4, 3), 0, 1, -1, 0], [0, -1, 0, 1, 0],
            [0, -p, 0, p, 1], [0, -mu-ah, 0, mu, 1], [1, 0, 0, 0, 0],
            [CL, -1, 0, 0, 0], [-CU, 1, 0, 0, 0],
        ]
        rhs = [0, 0, PB-lo, 1, F(3, 2), 1, F(4, 3), 0, 0,
               ah*(PB-lo), 1, dh, -dl]
        objective = [0, 0, lam-saving, 0, 1]
        caps = [1, CB, 1, CB, p*CB]
        weights = list(map(F, cell["weights"]))
        require(len(weights) == 13 and all(v >= 0 for v in weights), "dual signs")
        residual = [max(F(0), objective[j] - sum(
            weights[k]*matrix[k][j] for k in range(13))) for j in range(5)]
        require(residual == list(map(F, cell["residual"])), "residual replay")
        upper = 1 + lam*(hi-1) + sum(weights[k]*rhs[k] for k in range(13))
        upper += sum(residual[j]*caps[j] for j in range(5))
        require(upper == F(cell["upper"]), "stored upper replay")
        require(upper < F(13, 8), f"rectangle {index}: target bound")
        bounds.append(upper)
    require(proof["rectangles"] == len(cells), "rectangle summary")
    require(proof["nonempty"] == len(bounds), "nonempty summary")
    require(F(proof["max_upper"]) == max(bounds), "maximum summary")
    return {"status": "PASS", "target": "13/8", "rectangles": len(cells),
            "nonempty": len(bounds), "certified_empty": empty,
            "max_low_grid_upper_exact": str(max(bounds)),
            "max_low_grid_upper_display": float(max(bounds)),
            "high_grid_upper_display": float(high_grid_upper),
            "high_grid_strict_target": True, "power_bottleneck_strict_target": True,
            "arithmetic": "fractions.Fraction, signed Taylor remainder bounds"}


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
