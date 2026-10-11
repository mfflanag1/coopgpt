import unittest
from fractions import Fraction as Q
from itertools import product
from model import Technology, standalone_first


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.model = Technology()

    def test_dual_representation_independently_derived(self):
        self.assertEqual(self.model.dual_vertices, ((0, 0, 3), (2, 0, 2), (6, 2, 0)))
        for h, l, e in product(range(4), range(4), range(8)):
            self.assertEqual(self.model.value((h, l, e)), min(6*h+2*l, 2*h+2*e, 3*e))

    def test_exact_fractional_schedule(self):
        bundles = ((Q(1,2), 0, Q(1,2)), (0, 1, 1), (1, Q(1,2), Q(1,2)), (0,0,1))
        s = self.model.schedule(bundles, installed=((1,0),(0,1),(1,1),(0,0)))
        self.assertEqual(s['service_capacity_value'], 9)
        self.assertEqual(s['incremental_energy_kwh'], 3)
        self.assertLessEqual(s['peak_node_kw'], s['safe_nonbinding_feeder_kw'])
        self.assertEqual(s['warm_baseline_energy_kwh'], Q(2,5))
        self.assertFalse(s['request_level_SLA_verified'])

    def test_standalone_first_can_waste_valuable_energy(self):
        result = standalone_first(self.model, ((1,0,0), (0,1,2)))
        self.assertEqual(result['autarky'], 2)
        self.assertEqual(result['standalone_first'], 5)
        self.assertEqual(result['joint'], 6)

    def test_zero_reports_preserve_committed_idle_accounting(self):
        s = self.model.schedule(((0,0,0), (0,0,0)), installed=((1,1),(1,1)))
        self.assertEqual(s['service_capacity_value'], 0)
        self.assertEqual(s['total_node_energy_kwh'], Q(2,5))
        self.assertEqual(s['peak_node_kw'], Q(2,5))

    def test_report_must_fit_fixed_physical_inventory(self):
        with self.assertRaises(ValueError):
            self.model.schedule(((Q(3,2),0,1),), installed=((1,0),))

    def test_underreport_cannot_change_installed_inventory(self):
        installed = ((1,1),(1,1))
        full = self.model.schedule(((1,1,2),(1,1,1)), installed)
        low = self.model.schedule(((0,0,0),(1,1,1)), installed)
        self.assertEqual(full['warm_baseline_energy_kwh'], low['warm_baseline_energy_kwh'])
        self.assertEqual(full['safe_nonbinding_feeder_kw'], low['safe_nonbinding_feeder_kw'])
        with self.assertRaises(TypeError):
            self.model.schedule(((0,0,0),))


if __name__ == '__main__':
    unittest.main()
