"""Independent small fixtures for unit conversion, calibration and hidden outcomes."""
import csv
import math
from pathlib import Path
import tempfile
import unittest

from prepare_melodi import input_bin, nearest_rank
from run_study import independently_check, training_reference
from replay import Job, Service
from watt_validation import fit


class AnalysisTests(unittest.TestCase):
    def test_checker_rejects_double_reservation_despite_feasible_actual_cost(self):
        jobs = [Job(str(i), 0, 10, {s:Service(1,6) for s in (0,1)},
                    {s:Service(1,1) for s in (0,1)}) for i in (0,1)]
        # Each job actually costs one joule, but their simultaneous six-joule
        # reservations cannot both fit the shared ten-joule account.
        result = {'mode':'pool', 'records':[
            {'id':str(i), 'server':i, 'start':0, 'slot_end':1,
             'response_end':1,'outcome':'ontime'} for i in (0,1)],
            'rejections':[], 'ontime':2, 'late':0, 'total_energy_j':2,
            'initial_budgets_j':[5,5], 'remaining_accounts_j':[8]}
        with self.assertRaisesRegex(ValueError, 'chronological energy reservation'):
            independently_check(result, jobs)

    def test_unconstrained_energy_fit_positive_and_negative(self):
        for idle, marginal in ((4., 2.), (3., -1.)):
            rows = [{'duration_s': t, 'request_count': n,
                     'energy_j': idle*t+marginal*n}
                    for t, n in ((10, 1), (10, 3), (12, 5), (11, 2))]
            found = fit(rows)
            self.assertAlmostEqual(found[0], idle)
            self.assertAlmostEqual(found[1], marginal)

    def test_singular_energy_fit_rejected(self):
        with self.assertRaises(ValueError):
            fit([{'duration_s':10, 'request_count':2, 'energy_j':40}]*4)

    def test_fixed_bin_boundaries_and_empirical_quantile(self):
        self.assertEqual(input_bin(31), '[0,32)')
        self.assertEqual(input_bin(32), '[32,64)')
        self.assertEqual(input_bin(64), '[64,128)')
        self.assertEqual(input_bin(128), '[128,256)')
        self.assertEqual(input_bin(256), '[256,infinity)')
        self.assertEqual(nearest_rank(list(range(1,11))), 9)

    def test_budget_reference_excludes_holdout_and_noncomparable_rows(self):
        common = {'same_prompt_tokens':'1', 'same_response_text':'1'}
        for h in ('laptop2','workstation'):
            common.update({h+'_total_duration_seconds':'5',
                           h+'_energy_gpu_kwh':'1', h+'_load_fraction':'0.01'})
        good = {**common, 'prompt_sha256':'00000001'+'0'*56}
        holdout = {**common, 'prompt_sha256':'00000000'+'0'*56,
                   'laptop2_energy_gpu_kwh':'1000'}
        unmatched = {**common, 'prompt_sha256':'00000002'+'0'*56,
                     'same_response_text':'0','workstation_energy_gpu_kwh':'1000'}
        cold = {**common, 'prompt_sha256':'00000003'+'0'*56,
                'laptop2_load_fraction':'0.011'}
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'pairs.csv'
            with p.open('w',newline='') as f:
                writer = csv.DictWriter(f,fieldnames=list(good))
                writer.writeheader(); writer.writerows([good, holdout, unmatched, cold])
            joules, count = training_reference(p)
        self.assertEqual(count, 1)
        self.assertEqual(joules, 3_600_000.)


if __name__ == '__main__':
    unittest.main()
