#!/usr/bin/env python3
"""Check the exact weighted identities completing packet class 11.

The relay's activations are proved separately in the paper note.  This checker
covers the remaining blocker classification with four source-specific tables:
two exceptional opposite cuts and four q cuts at the first Lmax exchange,
fifteen q cuts at the second Lmax exchange, and all sixteen q cuts at the
terminal Lmin exchange.  It uses pure rational coefficient arithmetic, makes
no solver call, and imports no production encoder.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import combinations
from math import lcm
from pathlib import Path


RAW_ROWS = [
  {
    "coalition": [
      0,
      5
    ],
    "eq": {
      "sumx": "2/3",
      "sumz": "-1/3"
    },
    "hypothetical_source": "Co",
    "ineq": {
      "Co": "2/3",
      "P5o": "1/3",
      "x0<=x4": "2/3",
      "x0<=x5": "1/3",
      "z0>=0": "4/3",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z4<=z1": "1/3"
    },
    "stage": "first-opposite-exception"
  },
  {
    "coalition": [
      0,
      1,
      5
    ],
    "eq": {
      "sumz": "1/3"
    },
    "hypothetical_source": "Co",
    "ineq": {
      "Co": "1/3",
      "P4o": "1/3",
      "P5o": "1",
      "x0<=x2": "1/3",
      "x0<=x4": "1/3",
      "x0<=x5": "2/3",
      "z0>=0": "5/3",
      "z3>=0": "1/3",
      "z5<=z1": "1/3"
    },
    "stage": "first-opposite-exception"
  },
  {
    "coalition": [
      1
    ],
    "eq": {
      "q1": "1/3",
      "sumx": "1/3"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "Cq": "1/3",
      "P5o": "2/3",
      "x0<=x5": "2/3",
      "x4>=0": "1/3",
      "x5>=0": "1/3",
      "z0>=0": "1",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "2/3"
    },
    "stage": "first-q-filter"
  },
  {
    "coalition": [
      0,
      1
    ],
    "eq": {
      "q1": "1/3",
      "sumq": "1/3"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "Cq": "1/3",
      "P5o": "2/3",
      "P5q": "1/3",
      "q4>=0": "1/3",
      "x0<=x5": "1",
      "z0>=0": "4/3",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "2/3"
    },
    "stage": "first-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      4
    ],
    "eq": {
      "q1": "1/3",
      "sumq": "1/3",
      "sumx": "1/3",
      "sumz": "-1/3"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "Cq": "1/3",
      "P5o": "1/3",
      "P5q": "1/3",
      "x0<=x5": "2/3",
      "x4>=0": "1/3",
      "x5>=0": "1/3",
      "z0>=0": "1",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "2/3"
    },
    "stage": "first-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      3,
      5
    ],
    "eq": {
      "q1": "1/3",
      "sumq": "1/3"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "Cq": "1/3",
      "P4q": "1/3",
      "P5o": "1",
      "d1>=0": "1/3",
      "x0<=x5": "1",
      "x2>=0": "1/3",
      "x4>=0": "1/3",
      "z0>=0": "4/3",
      "z3>=0": "1/3",
      "z5<=z1": "2/3"
    },
    "stage": "first-q-filter"
  },
  {
    "coalition": [
      1
    ],
    "eq": {
      "q1": "1/3",
      "sumx": "1/3"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "Cq": "1/3",
      "P5o": "2/3",
      "x0<=x4": "1/3",
      "x0<=x5": "1/3",
      "x5>=0": "2/3",
      "z0>=0": "1",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "2/3"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      0,
      1
    ],
    "eq": {
      "q1": "1/3",
      "sumq": "1/3"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "Cq": "1/3",
      "P5o": "2/3",
      "P5q": "1/3",
      "q4>=0": "1/3",
      "x0<=x5": "1",
      "z0>=0": "4/3",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "2/3"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      1,
      3
    ],
    "eq": {
      "q1": "1/3",
      "sumq": "1/3"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1q": "1/3",
      "Cq": "1/3",
      "P5o": "1",
      "q4>=0": "1/3",
      "x0<=x5": "1",
      "z0>=0": "4/3",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "2/3"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      1,
      4
    ],
    "eq": {
      "q1": "1/3",
      "sumq": "1/3",
      "sumx": "1/3",
      "sumz": "-1/3"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "Cq": "1/3",
      "P5o": "1/3",
      "P5q": "1/3",
      "q0>=0": "1/3",
      "x0<=x4": "1/3",
      "x0<=x5": "1/3",
      "x5>=0": "2/3",
      "z0>=0": "2/3",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "2/3"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      1,
      5
    ],
    "eq": {
      "q1": "1/6",
      "sumq": "1/6",
      "sumx": "1/6"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "1/6",
      "Cq": "1/6",
      "P4q": "1/6",
      "P5o": "5/6",
      "q0>=0": "1/6",
      "q3>=0": "1/6",
      "x0<=x4": "1/3",
      "x0<=x5": "2/3",
      "x5>=0": "1/6",
      "z0>=0": "7/6",
      "z2>=0": "1/3",
      "z3>=0": "1/6",
      "z5<=z1": "1/2"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      4
    ],
    "eq": {
      "q1": "1/3",
      "sumq": "1/3",
      "sumx": "1/3",
      "sumz": "-1/3"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "Cq": "1/3",
      "P5o": "1/3",
      "P5q": "1/3",
      "x0<=x5": "2/3",
      "x4>=0": "1/3",
      "x5>=0": "1/3",
      "z0>=0": "1",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "2/3"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      5
    ],
    "eq": {
      "q1": "1/6",
      "sumq": "1/6",
      "sumx": "1/6"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "1/6",
      "Cq": "1/6",
      "P4q": "1/6",
      "P5o": "5/6",
      "q3>=0": "1/6",
      "x0<=x4": "1/3",
      "x0<=x5": "2/3",
      "x5>=0": "1/6",
      "z0>=0": "4/3",
      "z2>=0": "1/3",
      "z3>=0": "1/6",
      "z5<=z1": "1/2"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      1,
      3,
      4
    ],
    "eq": {
      "q1": "1/3",
      "sumq": "1/3",
      "sumx": "1/3",
      "sumz": "-1/3"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1q": "1/3",
      "Cq": "1/3",
      "P5o": "2/3",
      "x0<=x4": "1/3",
      "x0<=x5": "1/3",
      "x5>=0": "2/3",
      "z0>=0": "1",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "2/3"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      1,
      3,
      5
    ],
    "eq": {
      "q1": "1/6",
      "sumq": "1/6",
      "sumx": "1/6"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "1/6",
      "Cq": "1/6",
      "P4q": "1/6",
      "P5o": "5/6",
      "q0>=0": "1/6",
      "x0<=x4": "1/3",
      "x0<=x5": "2/3",
      "x5>=0": "1/6",
      "z0>=0": "7/6",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "1/2"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      1,
      4,
      5
    ],
    "eq": {
      "q1": "1/6",
      "sumq": "1/3",
      "sumx": "1/6",
      "sumz": "-1/6"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "1/6",
      "Cq": "1/6",
      "P4q": "1/6",
      "P5o": "2/3",
      "P5q": "1/6",
      "q0>=0": "1/3",
      "q3>=0": "1/6",
      "x0<=x4": "1/3",
      "x0<=x5": "2/3",
      "x5>=0": "1/6",
      "z0>=0": "1",
      "z2>=0": "1/3",
      "z3>=0": "1/6",
      "z5<=z1": "1/2"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      3,
      4
    ],
    "eq": {
      "q1": "2/9",
      "sumq": "1/3",
      "sumx": "1/9",
      "sumz": "-1/9"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "2/9",
      "B1q": "1/9",
      "Cq": "2/9",
      "P4o": "1/9",
      "P4q": "1/9",
      "P5o": "7/9",
      "P5q": "1/9",
      "q5>=0": "1/9",
      "x0<=x4": "1/3",
      "x0<=x5": "7/9",
      "z0>=0": "13/9",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "5/9"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      3,
      5
    ],
    "eq": {
      "q1": "1/6",
      "sumq": "1/6",
      "sumx": "1/6"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "1/6",
      "Cq": "1/6",
      "P4q": "1/6",
      "P5o": "5/6",
      "x0<=x4": "1/3",
      "x0<=x5": "2/3",
      "x5>=0": "1/6",
      "z0>=0": "4/3",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "1/2"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      4,
      5
    ],
    "eq": {
      "q1": "1/6",
      "sumq": "1/3",
      "sumx": "1/6",
      "sumz": "-1/6"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "1/6",
      "Cq": "1/6",
      "P4q": "1/6",
      "P5o": "2/3",
      "P5q": "1/6",
      "q0>=0": "1/6",
      "q3>=0": "1/6",
      "x0<=x4": "1/6",
      "x0<=x5": "5/6",
      "x4>=0": "1/6",
      "z0>=0": "7/6",
      "z2>=0": "1/3",
      "z3>=0": "1/6",
      "z5<=z1": "1/2"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      1,
      3,
      4,
      5
    ],
    "eq": {
      "q1": "1/6",
      "sumq": "1/3",
      "sumx": "1/6",
      "sumz": "-1/6"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "1/6",
      "Cq": "1/6",
      "P4q": "1/6",
      "P5o": "2/3",
      "P5q": "1/6",
      "q0>=0": "1/3",
      "x0<=x4": "1/3",
      "x0<=x5": "2/3",
      "x5>=0": "1/6",
      "z0>=0": "1",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "1/2"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      3,
      4,
      5
    ],
    "eq": {
      "q1": "1/6",
      "sumq": "1/3",
      "sumx": "1/6",
      "sumz": "-1/6"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "1/6",
      "Cq": "1/6",
      "P4q": "1/6",
      "P5o": "2/3",
      "P5q": "1/6",
      "q0>=0": "1/6",
      "x0<=x4": "1/6",
      "x0<=x5": "5/6",
      "x4>=0": "1/6",
      "z0>=0": "7/6",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "1/2"
    },
    "stage": "second-q-filter"
  },
  {
    "coalition": [
      1
    ],
    "eq": {
      "q1": "1/3",
      "sumx": "1/3"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "Cq": "1/3",
      "P5o": "2/3",
      "d1>=0": "1/3",
      "x0<=x4": "1/3",
      "x0<=x5": "1/3",
      "x5>=0": "2/3",
      "z0>=0": "1",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "2/3"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      0,
      1
    ],
    "eq": {
      "q1": "1/3",
      "sumq": "1/3"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "Cq": "1/3",
      "P5o": "2/3",
      "P5q": "1/3",
      "d1>=0": "1/3",
      "q4>=0": "1/3",
      "x0<=x5": "2/3",
      "x5>=0": "1/3",
      "z0>=0": "1",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "2/3"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      1,
      3
    ],
    "eq": {
      "q1": "1/6",
      "sumq": "1/6",
      "sumz": "1/6"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1q": "1/6",
      "Cq": "1/6",
      "P4o": "1/6",
      "P5o": "5/6",
      "d1>=0": "1/6",
      "q4>=0": "1/6",
      "x0<=x4": "1/6",
      "x0<=x5": "5/6",
      "z0>=0": "4/3",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "1/2"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      1,
      4
    ],
    "eq": {
      "q1": "1/7",
      "sumq": "2/21",
      "sumx": "1/21",
      "sumz": "4/21"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "4/21",
      "B1q": "1/21",
      "B2q": "1/21",
      "Cq": "2/21",
      "P4o": "4/21",
      "P5o": "19/21",
      "P5q": "1/21",
      "d1>=0": "2/21",
      "x0<=x4": "1/3",
      "x0<=x5": "17/21",
      "z0>=0": "31/21",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "10/21"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      1,
      5
    ],
    "eq": {
      "q1": "1/6",
      "sumq": "1/12",
      "sumx": "1/12",
      "sumz": "1/6"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "1/4",
      "B2q": "1/12",
      "Cq": "1/12",
      "P4o": "1/6",
      "P4q": "1/12",
      "P5o": "11/12",
      "d1>=0": "1/12",
      "x0<=x4": "1/3",
      "x0<=x5": "5/6",
      "z0>=0": "3/2",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "1/2"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      3
    ],
    "eq": {
      "q1": "1/3",
      "sumq": "1/3"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "Cq": "1/3",
      "P4q": "1/3",
      "P5o": "2/3",
      "d1>=0": "1/3",
      "q5>=0": "1/3",
      "x0<=x4": "1/3",
      "x0<=x5": "1/3",
      "x5>=0": "1/3",
      "z0>=0": "1",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "2/3"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      4
    ],
    "eq": {
      "q1": "1/3",
      "sumq": "1/3"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "Cq": "1/3",
      "P5o": "2/3",
      "P5q": "1/3",
      "d1>=0": "1/3",
      "x0<=x5": "2/3",
      "x4>=0": "1/3",
      "x5>=0": "1/3",
      "z0>=0": "1",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "2/3"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      5
    ],
    "eq": {
      "q1": "2/9",
      "sumq": "2/9",
      "sumz": "1/9"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "2/9",
      "B2q": "1/9",
      "Cq": "1/9",
      "P4o": "1/9",
      "P4q": "1/9",
      "P5o": "8/9",
      "P5q": "1/9",
      "d1>=0": "1/9",
      "q4>=0": "1/9",
      "x0<=x4": "2/9",
      "x0<=x5": "8/9",
      "z0>=0": "13/9",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "5/9"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      1,
      3,
      4
    ],
    "eq": {
      "q1": "1/6",
      "sumq": "1/6",
      "sumz": "1/6"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1q": "1/6",
      "Cq": "1/6",
      "P4o": "1/6",
      "P5o": "5/6",
      "d1>=0": "1/6",
      "x0<=x4": "1/6",
      "x0<=x5": "5/6",
      "x4>=0": "1/6",
      "z0>=0": "4/3",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "1/2"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      1,
      3,
      5
    ],
    "eq": {
      "q1": "1/6",
      "sumq": "1/6",
      "sumz": "1/6"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "1/6",
      "Cq": "1/6",
      "P4o": "1/6",
      "P4q": "1/6",
      "P5o": "5/6",
      "d1>=0": "1/6",
      "q0>=0": "1/6",
      "x0<=x4": "1/3",
      "x0<=x5": "5/6",
      "z0>=0": "4/3",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "1/2"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      1,
      4,
      5
    ],
    "eq": {
      "q1": "5/27",
      "sumq": "4/27",
      "sumx": "1/27",
      "sumz": "4/27"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "2/9",
      "B1q": "1/27",
      "B2q": "1/9",
      "Cq": "2/27",
      "P4o": "4/27",
      "P4q": "2/27",
      "P5o": "25/27",
      "P5q": "1/27",
      "d1>=0": "2/27",
      "x0<=x4": "1/3",
      "x0<=x5": "23/27",
      "z0>=0": "41/27",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "14/27"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      3,
      4
    ],
    "eq": {
      "q1": "2/9",
      "sumq": "1/3",
      "sumx": "-1/9",
      "sumz": "1/9"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1q": "1/9",
      "Cq": "2/9",
      "P4o": "1/9",
      "P4q": "1/9",
      "P5o": "7/9",
      "P5q": "1/9",
      "d1>=0": "2/9",
      "q5>=0": "1/9",
      "x0<=x4": "1/9",
      "x0<=x5": "7/9",
      "x4>=0": "2/9",
      "z0>=0": "11/9",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "5/9"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      3,
      5
    ],
    "eq": {
      "q1": "1/9",
      "sumq": "1/9",
      "sumz": "2/9"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "2/9",
      "Cq": "1/9",
      "P4o": "2/9",
      "P4q": "1/9",
      "P5o": "8/9",
      "d1>=0": "1/9",
      "x0<=x4": "1/3",
      "x0<=x5": "7/9",
      "z0>=0": "13/9",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "4/9"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      4,
      5
    ],
    "eq": {
      "q1": "1/6",
      "sumq": "1/6",
      "sumz": "1/6"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "1/4",
      "B2q": "1/12",
      "Cq": "1/12",
      "P4o": "1/6",
      "P4q": "1/12",
      "P5o": "11/12",
      "P5q": "1/12",
      "d1>=0": "1/12",
      "x0<=x4": "1/3",
      "x0<=x5": "5/6",
      "z0>=0": "3/2",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "1/2"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      1,
      3,
      4,
      5
    ],
    "eq": {
      "q1": "1/6",
      "sumq": "1/6",
      "sumz": "1/6"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "1/6",
      "B1q": "1/12",
      "B2q": "1/12",
      "Cq": "1/12",
      "P4o": "1/6",
      "P4q": "1/12",
      "P5o": "11/12",
      "d1>=0": "1/12",
      "x0<=x4": "1/3",
      "x0<=x5": "5/6",
      "z0>=0": "3/2",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "1/2"
    },
    "stage": "terminal-q-filter"
  },
  {
    "coalition": [
      0,
      1,
      3,
      4,
      5
    ],
    "eq": {
      "q1": "1/7",
      "sumq": "4/21",
      "sumx": "-1/21",
      "sumz": "4/21"
    },
    "hypothetical_source": "Cq",
    "ineq": {
      "B1o": "4/21",
      "B1q": "1/21",
      "B2q": "1/21",
      "Cq": "2/21",
      "P4o": "4/21",
      "P4q": "2/21",
      "P5o": "19/21",
      "P5q": "1/21",
      "d1>=0": "2/21",
      "x0<=x4": "1/3",
      "x0<=x5": "17/21",
      "z0>=0": "31/21",
      "z2>=0": "1/3",
      "z3>=0": "1/3",
      "z5<=z1": "10/21"
    },
    "stage": "terminal-q-filter"
  }
]

H1 = (0, -1, 1, 1, 0, -1)
H2 = (0, -1, 1, 0, 0, 0)
B1 = (0, 1, 2, 5)
B2 = (0, 1, 3)
FIRST_STRUCTURAL_CANDIDATES = {
    (1,),
    (0, 1),
    (0, 5),
    (0, 1, 4),
    (0, 1, 5),
    B1,
    (0, 1, 3, 5),
}
FIRST_OPPOSITE_CANDIDATES = {
    (1,),
    (0, 1),
    (0, 1, 4),
    B1,
    (0, 1, 3, 5),
}


def linear(*terms):
    result = {}
    for multiplier, form in terms:
        multiplier = Fraction(multiplier)
        for name, coefficient in form.items():
            value = result.get(name, Fraction(0)) + multiplier * coefficient
            if value:
                result[name] = value
            else:
                result.pop(name, None)
    return result


def variable(name):
    return {name: Fraction(1)}


def constant(value):
    value = Fraction(value)
    return {"constant": value} if value else {}


def point_sum(point, players):
    return linear(*((1, point[player]) for player in players))


def eligible(direction):
    rows = []
    for size in range(1, 6):
        for coalition in combinations(range(6), size):
            if sum(direction[player] for player in coalition) < 0:
                rows.append(coalition)
    return rows


def named_system(row):
    x = [variable(f"x{player}") for player in range(6)]
    z = [variable(f"z{player}") for player in range(6)]
    q = [variable(f"q{player}") for player in range(6)]
    inequalities = {}
    for name, point in (("x", x), ("z", z), ("q", q)):
        for player in range(6):
            inequalities[f"{name}{player}>=0"] = linear((-1, point[player]))
    for player in range(4):
        inequalities[f"d{player}>=0"] = linear((1, z[player]), (-1, x[player]))
    for player in (4, 5):
        inequalities[f"delta{player}>=0"] = linear(
            (1, x[player]), (-1, z[player])
        )
    for player in range(1, 6):
        inequalities[f"x0<=x{player}"] = linear((1, x[0]), (-1, x[player]))
    for player in (0, 2, 3, 4, 5):
        inequalities[f"z{player}<=z1"] = linear((1, z[player]), (-1, z[1]))

    def comparison(prefix, coalition, left, right):
        inequalities[prefix] = linear(
            (1, point_sum(left, coalition)), (-1, point_sum(right, coalition))
        )

    p4 = (1, 2, 4)
    p5 = (1, 2, 3, 5)
    comparison("P4o", p4, x, z)
    comparison("P4q", p4, x, q)
    comparison("P5o", p5, x, z)
    comparison("P5q", p5, x, q)
    comparison("B1o", B1, z, x)
    comparison("B1q", B1, z, q)
    comparison("B2o", B2, z, x)
    comparison("B2q", B2, z, q)

    coalition = tuple(row["coalition"])
    stage = row["stage"]
    if stage == "first-opposite-exception":
        comparison("Co", coalition, z, x)
        allowed_branches = set()
    elif stage in ("first-q-filter", "second-q-filter"):
        comparison("Cq", coalition, z, q)
        allowed_branches = {"B1o", "B1q"} if stage == "second-q-filter" else set()
    elif stage == "terminal-q-filter":
        comparison("Cq", coalition, x, q)
        allowed_branches = {"B1o", "B1q", "B2o", "B2q"}
    else:
        raise AssertionError(f"unknown stage {stage}")

    branch_names = {"B1o", "B1q", "B2o", "B2q"}
    for name in branch_names - allowed_branches:
        inequalities.pop(name)

    equalities = {
        "sumx": linear((1, point_sum(x, range(6))), (-1, constant(1))),
        "sumz": linear((1, point_sum(z, range(6))), (-1, constant(1))),
        "sumq": linear((1, point_sum(q, range(6))), (-1, constant(1))),
        "q1": q[1],
    }
    distance = linear(
        (1, point_sum(x, (0, 1, 2, 3))),
        (-1, point_sum(z, (0, 1, 2, 3))),
    )
    return inequalities, equalities, distance


def scaled_integer_row(row):
    values = [
        *(Fraction(value) for value in row["ineq"].values()),
        *(Fraction(value) for value in row["eq"].values()),
    ]
    scale = 1
    for value in values:
        scale = lcm(scale, value.denominator)
    return {
        "stage": row["stage"],
        "coalition": row["coalition"],
        "hypothetical_source": row["hypothetical_source"],
        "integer_scale": scale,
        "inequality_multipliers": {
            name: int(Fraction(value) * scale) for name, value in row["ineq"].items()
        },
        "equality_multipliers": {
            name: int(Fraction(value) * scale) for name, value in row["eq"].items()
        },
        "identity": f"weighted sum = {scale}*(D-1/3)",
    }


def verify_row(row):
    inequalities, equalities, distance = named_system(row)
    terms = []
    for name, multiplier in row["ineq"].items():
        if name not in inequalities or Fraction(multiplier) < 0:
            raise AssertionError(f"bad inequality term {name}={multiplier}")
        terms.append((Fraction(multiplier), inequalities[name]))
    for name, multiplier in row["eq"].items():
        if name not in equalities:
            raise AssertionError(f"bad equality term {name}")
        terms.append((Fraction(multiplier), equalities[name]))
    expression = linear(*terms)
    target = linear((1, distance), (-1, constant(Fraction(1, 3))))
    residual = linear((1, expression), (-1, target))
    if residual:
        raise AssertionError(f"certificate identity failed: {residual}")
    return scaled_integer_row(row)


def audit_exhaustiveness():
    grouped = {}
    for row in RAW_ROWS:
        grouped.setdefault(row["stage"], []).append(tuple(row["coalition"]))
    expected = {
        "first-opposite-exception": sorted(((0, 5), (0, 1, 5))),
        "first-q-filter": sorted(FIRST_OPPOSITE_CANDIDATES - {B1}),
        "second-q-filter": sorted(set(eligible(H2)) - {B2}),
        "terminal-q-filter": sorted(eligible(H2)),
    }
    for stage, coalitions in expected.items():
        actual = sorted(grouped.get(stage, []))
        if actual != coalitions or len(actual) != len(set(actual)):
            raise AssertionError(f"nonexhaustive {stage}: {actual}")
    if len(eligible(H1)) != 20 or len(FIRST_STRUCTURAL_CANDIDATES) != 7:
        raise AssertionError("first-stage structural cut census changed")
    if len(eligible(H2)) != 16:
        raise AssertionError("one-for-one cut census changed")
    return {stage: len(coalitions) for stage, coalitions in expected.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    counts = audit_exhaustiveness()
    rows = [verify_row(row) for row in RAW_ROWS]

    mutated = {
        **RAW_ROWS[0],
        "ineq": {**RAW_ROWS[0]["ineq"], "Co": "1"},
    }
    try:
        verify_row(mutated)
    except AssertionError:
        mutation_control = "rejected coefficient perturbation"
    else:
        raise AssertionError("mutation control unexpectedly passed")

    payload = {
        "schema": "strict-exchange-p4-class11-hand-certificates-v1",
        "status": "PASS",
        "scope": (
            "thirty-seven source-specific exact weighted identities completing "
            "the class-11 blocker relay; pure rational coefficient arithmetic, "
            "no solver call, and no production encoder import"
        ),
        "first_eligible_cut_count": len(eligible(H1)),
        "first_structural_candidate_count": len(FIRST_STRUCTURAL_CANDIDATES),
        "first_structural_candidates": [list(c) for c in sorted(FIRST_STRUCTURAL_CANDIDATES)],
        "first_opposite_candidate_count": len(FIRST_OPPOSITE_CANDIDATES),
        "first_opposite_candidates": [list(c) for c in sorted(FIRST_OPPOSITE_CANDIDATES)],
        "certificate_counts": counts,
        "certificate_count": len(rows),
        "mutation_control": mutation_control,
        "rows": rows,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
