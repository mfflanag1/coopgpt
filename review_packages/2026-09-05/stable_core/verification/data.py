"""Strict data handling and validation guards, active even under python -O."""
import json
from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(str(message))


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def strict_json_load(stream):
    return json.load(stream, object_pairs_hook=unique_object)


def members(coalition, n):
    return [i for i in range(n) if coalition >> i & 1]


def parse_coalition(name, n):
    require(isinstance(name, str) and name.startswith("{") and name.endswith("}"),
            "coalition must use braces")
    require(bool(name[1:-1]), "empty coalition must not be in the nonempty table")
    coalition = 0
    for token in name[1:-1].split(","):
        player = int(token)
        require(1 <= player <= n, "player out of range")
        mask = 1 << (player - 1)
        require(not coalition & mask, "repeated player in coalition")
        coalition |= mask
    return coalition


def parse_game(table, n):
    values = [Fraction(0)] * (1 << n)
    seen = set()
    for name, value in table.items():
        coalition = parse_coalition(name, n)
        require(coalition not in seen, "duplicate coalition after parsing")
        require(isinstance(value, str), "rational values must be strings")
        seen.add(coalition)
        values[coalition] = Fraction(value)
    require(seen == set(range(1, 1 << n)), "incomplete nonempty coalition table")
    return values
