from fractions import Fraction as F
import unittest
from analyze_panel import calculate, quantile, analyze, NODES


def row(sid, nav='10000', dv01='0', dv100='0'):
    return {'series_id': sid, 'accession': '0000000001-25-000001', 'cik': '1',
            'series_name': sid, 'nav': nav, 'all_zero_vector': dv01 == dv100 == '0',
            'raw_metrics': {f'INTRST_RATE_CHANGE_{n}_{m}': v
                            for n in NODES for m, v in [('DV01', dv01), ('DV100', dv100)]}}


class AnalysisTests(unittest.TestCase):
    def test_known_decimal_example(self):
        r = row('test', '20237340.35', '10', '550')
        c = calculate(r)
        self.assertEqual(c['nodes'][0]['residual_exact'], '-450')
        self.assertEqual(F(c['primary_exact']), F(450000000, 2023734035))
        self.assertEqual(F(c['nodes'][0]['relative_exact']), F(9, 20))

    def test_zero_denominators_and_signs(self):
        c = calculate(row('test', dv100='-10'))
        self.assertIsNone(c['nodes'][0]['relative'])
        self.assertEqual(c['nodes'][0]['residual_exact'], '-10')
        self.assertEqual(c['primary_exact'], '10')
        self.assertEqual(c['vector_exact'], '50')

    def test_quantiles(self):
        self.assertEqual(quantile([F(0), F(10)], [F(1), F(1)], F(1, 2)), 0)
        self.assertEqual(quantile([F(0), F(10)], [F(1), F(9)], F(1, 2)), 10)
        with self.assertRaises(ValueError): quantile([F(1)], [F(0)], F(1, 2))

    def test_ties_thresholds_weights_and_zero_retention(self):
        rs = [row(f'S{i:09d}', dv100='10') for i in range(25)]
        rs += [row('S999999998'), row('S999999999', nav='1000000', dv100='1010')]
        pre = {'status': 'preflight_only', 'candidates': rs, 'exclusion_counts': {}}
        s, computed, audit = analyze(pre)
        self.assertEqual(s['sample_count'], 27)
        self.assertEqual(s['all_zero_vectors'], 1)
        self.assertEqual(s['thresholds'][1]['fund_count'], 1)  # strict >10
        self.assertEqual(s['audit_selection']['top_20_plus_ties'], 26)
        self.assertEqual(s['primary_distribution_nav_bp']['nav_weighted']['median'], '10.1')
        self.assertEqual(s['source_validated_funds'], 0)


if __name__ == '__main__': unittest.main()
