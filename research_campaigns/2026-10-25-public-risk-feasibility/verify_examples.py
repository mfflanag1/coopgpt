#!/usr/bin/env python3
"""Reproduce two exploratory disclosure calculations; not a bulk N-PORT parser.

Print JSON to stdout. No network or file mutation. One example is manually
transcribed; the issuer example additionally has a preserved HTML source check.
"""
import hashlib
import json
import re
from decimal import Decimal, localcontext
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path

BASE = Path(__file__).resolve().parent


class TextReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.parts.append(" ".join(data.split()))


def following_value(text, anchor):
    """One unambiguous labelled field, failing closed if source layout changes."""
    if text.count(anchor) != 1:
        raise ValueError(f"Expected one field anchor: {anchor}")
    return text.split(anchor, 1)[1].strip().splitlines()[0].strip()


def parse_gladstone():
    raw = (BASE / "raw/gladstone_20241231.html").read_bytes()
    manifest = json.loads((BASE / "raw/gladstone_access.json").read_text())
    assert hashlib.sha256(raw).hexdigest() == manifest["sha256"]
    parser = TextReader()
    parser.feed(raw.decode())
    text = "\n".join(parser.parts)
    result = {
        "nav": following_value(text, "c. Net assets."),
        "report_date": following_value(text, "b. Date as of which information is reported."),
        "currency": following_value(text, "ISO Currency code"),
    }
    for name, end in [("DV01", "b. Interest Rate Risk (DV100)"),
                      ("DV100", "c. Credit Spread Risk")]:
        start = "Interest Rate Risk (" + name + ")"
        assert text.count(start) == 1
        part = text.split(start, 1)[1].split(end, 1)[0]
        # Match actual field rows, not the prose list of required maturities.
        matches = re.findall(r"(?:^|\n)(3 month|1 year|5 years|10 years|30 years)\.\n(-?\d+(?:\.\d+)?)(?=\n|$)", part)
        assert [x[0] for x in matches] == ["3 month", "1 year", "5 years", "10 years", "30 years"]
        result[name.lower()] = [x[1] for x in matches]
    return result


def calculate(example):
    assert len(example["nodes"]) == len(example["dv01"]) == len(example["dv100"]) == 5
    with localcontext() as ctx:
        ctx.prec = 50
        nav = Decimal(example["nav"])
        assert nav > 0
        assert Decimal(example["assets"]) - Decimal(example["liabilities"]) == nav
        nodes = []
        for node, one_s, hundred_s in zip(example["nodes"], example["dv01"], example["dv100"]):
            one, hundred = Decimal(one_s), Decimal(hundred_s)
            assert one.is_finite() and hundred.is_finite()
            residual = hundred - 100 * one
            exact = Fraction(hundred_s) - 100 * Fraction(one_s)
            assert Fraction(residual) == exact
            nav_fraction = 10000 * abs(exact) / Fraction(example["nav"])
            nav_bp = 10000 * abs(residual) / nav
            assert nav_bp == Decimal(nav_fraction.numerator) / Decimal(nav_fraction.denominator)
            nodes.append({
                "node": node, "residual_filed_dollars": str(residual),
                "residual_exact_fraction": str(exact),
                "abs_relative_to_100_dv01": None if one == 0 else str(abs(residual) / (100 * abs(one))),
                "abs_residual_nav_bp": str(nav_bp),
                "interpretation": "reported scaling only; not a validated shock loss"
            })
        total = sum(abs(Decimal(n["residual_filed_dollars"])) for n in nodes)
        return {
            "id": example["id"], "nodes": nodes,
            "sum_absolute_node_residual_filed_dollars": str(total),
            "vector_l1_discrepancy_nav_bp": str(10000 * total / nav),
            "max_node_discrepancy_nav_bp": str(max(Decimal(n["abs_residual_nav_bp"]) for n in nodes)),
            "not_a_joint_shock": True,
            "nav_reconciles": True
        }


def main():
    examples = json.loads((BASE / "examples.json").read_text())
    parsed = parse_gladstone()
    gladstone = next(x for x in examples if x["id"] == "gladstone_20241231")
    assert parsed["currency"] == "United States Dollar"
    for field in ["nav", "dv01", "dv100", "report_date"]:
        assert parsed[field] == gladstone[field], (field, parsed[field], gladstone[field])
    outputs = [calculate(x) for x in examples]
    assert Fraction(outputs[0]["sum_absolute_node_residual_filed_dollars"]) == Fraction(23, 200000)
    assert Fraction(outputs[1]["nodes"][0]["residual_filed_dollars"]) == -450
    assert Decimal(outputs[1]["nodes"][0]["abs_relative_to_100_dv01"]) == Decimal("0.45")
    assert all(n["abs_relative_to_100_dv01"] is None for n in outputs[1]["nodes"][1:])
    print(json.dumps({
        "status": "passed", "examples": outputs, "node_pairs_checked": 10,
        "source_hash_and_parser_check": "passed for Gladstone issuer HTML",
        "manual_transcription_limitation": "RBB values checked against web-rendered SEC source; no local raw source for independent reparsing",
        "sample_status": "two exploratory convenience filings, no population inference",
        "panel_status": "not acquired or analyzed"
    }, indent=2))


if __name__ == "__main__":
    main()
