"""Independent exact checks for the frozen saved-schedule sensitivity formulas.

These fixtures are synthetic mathematics tests, never new empirical outcomes.
Only this test module is owned by the independent test lane.
"""
from fractions import Fraction as F
import unittest
from analysis import Q, energy_account, uniform_frontier, timing_trace, thresholds


def record(start, end, energy):
    return {'start':F(start),'slot_end':F(end),'actual_energy_j':F(energy)}


def job(ident, start, duration, arrival, deadline):
    return {'id':ident,'t':F(start),'d':F(duration),'arrival':F(arrival),'deadline':F(deadline)}


class FragilityTests(unittest.TestCase):
    def test_decimal_conversion_preserves_serialized_decimal(self):
        self.assertEqual(Q(.1),F(1,10))
        self.assertEqual(Q('0.30000000000000004'),F(7500000000000001,25000000000000000))
        self.assertEqual(Q(F(2,3)),F(2,3))

    def test_measurement_windows_exclude_cooldown_without_doublecount(self):
        values=energy_account([record(0,6,50),record(8,14,70)],F(20))
        self.assertEqual(values['window_j'],120)
        self.assertEqual(values['window_s'],6)  # Each 6-second slot has a 3-second measured window.
        self.assertEqual(values['cooldown_s'],6)
        self.assertEqual(values['resident_gap_s'],8)
        self.assertEqual(values['omitted_s'],14)
        self.assertEqual(values['omitted_s'],values['cooldown_s']+values['resident_gap_s'])
        full_energy=values['window_j']+F(5)*values['omitted_s']
        self.assertEqual(full_energy,190)
        self.assertNotEqual(full_energy,120+5*20)  # Adding idle across the entire horizon double-counts.

    def test_no_job_node_is_resident_for_entire_horizon(self):
        values=energy_account([],F(17,2))
        self.assertEqual(values['window_j'],0)
        self.assertEqual(values['window_s'],0)
        self.assertEqual(values['cooldown_s'],0)
        self.assertEqual(values['omitted_s'],F(17,2))
        self.assertEqual(values['resident_gap_s'],F(17,2))

    def test_invalid_energy_slots_are_rejected(self):
        cases=[([record(-1,6,50)],10),([record(0,11,50)],10),
               ([record(3,2,50)],10),([record(0,3,50)],10),
               ([record(0,6,-1)],10),([record(0,6,50),record(5,12,70)],20)]
        for records,horizon in cases:
            with self.subTest(records=records,horizon=horizon):
                with self.assertRaises(ValueError):energy_account(records,F(horizon))

    def test_common_horizon_cancels_for_two_different_node_powers(self):
        aut=[[record(0,6,50)],[record(1,9,80)]]
        pooled=[[record(0,8,70)],[record(1,7,65)]]
        powers=[F(2),F(7)]
        deltas=[]
        for horizon in (30,1000):
            aa=[energy_account(rows,F(horizon)) for rows in aut]
            pp=[energy_account(rows,F(horizon)) for rows in pooled]
            delta=sum(p['window_j']+w*p['omitted_s']-a['window_j']-w*a['omitted_s'] for a,p,w in zip(aa,pp,powers))
            reduced=sum(p['window_j']-a['window_j']-w*(p['window_s']-a['window_s']) for a,p,w in zip(aa,pp,powers))
            self.assertEqual(delta,reduced)
            deltas.append(delta)
        self.assertEqual(deltas,[F(15),F(15)])

    def test_uniform_funding_frontier_and_zero_time_edges(self):
        cases=[([20,12],[4,6],F(2)),([-2,12],[4,6],F(-1,2)),
               ([0],[5],F(0)),([4,0],[0,0],None),
               ([-2],[0],F(-1)),([4,3],[0,2],F(3,2)),
               ([F(3,2)],[F(3,4)],F(2))]
        for slacks,omitted,expected in cases:
            with self.subTest(slacks=slacks,omitted=omitted):
                self.assertEqual(uniform_frontier(list(map(F,slacks)),list(map(F,omitted))),expected)

    def test_separate_and_pooled_funding_are_distinct_constraints(self):
        budgets=[F(100),F(100)];costs=[F(130),F(50)]
        separate=sum(max(F(0),e-b) for e,b in zip(costs,budgets))
        pooled=max(F(0),sum(costs)-sum(budgets))
        self.assertEqual(separate,30);self.assertEqual(pooled,0)
        self.assertEqual(uniform_frontier([b-e for b,e in zip(budgets,costs)],[F(5),F(5)]),-6)
        self.assertEqual(uniform_frontier([sum(budgets)-sum(costs)],[F(10)]),2)

    def test_slowdown_propagates_queue_instead_of_overlapping_fixed_starts(self):
        jobs=[job('first',0,2,0,8),job('second',6,1,1,10)]
        rows=timing_trace(jobs,F(2),F(1))
        self.assertEqual(rows[0]['end'],8)
        self.assertEqual(rows[1]['start'],8)
        self.assertEqual(rows[1]['response'],F(21,2))
        self.assertFalse(rows[1]['ontime'])
        invalid_fixed_start_response=F(6)+F(1,2)+F(2)*F(1)
        self.assertLess(invalid_fixed_start_response,10)
        self.assertGreater(rows[0]['end'],jobs[1]['t'])

    def test_gap_keeps_later_release_floor_and_own_job_threshold(self):
        jobs=[job('first',0,2,0,8),job('second',20,1,20,22)]
        rows=timing_trace(jobs,F(1),F(1));limits=thresholds(jobs,F(1))
        self.assertEqual(rows[1]['start'],20)
        self.assertEqual(rows[1]['response'],F(43,2))
        self.assertEqual(limits[1]['critical'],F(3,2))
        self.assertEqual(limits[1]['witness_id'],'second')

    def test_exact_threshold_equality_and_neighboring_values(self):
        jobs=[job('first',0,2,0,8),job('second',6,1,1,10)]
        threshold=thresholds(jobs,F(1))[1]
        self.assertEqual(threshold['critical'],F(11,6))
        self.assertEqual(threshold['witness_id'],'first')
        self.assertEqual(threshold['numerator']/threshold['denominator'],threshold['critical'])
        at=timing_trace(jobs,threshold['critical'],F(1))[1]
        self.assertEqual(at['response'],10);self.assertTrue(at['ontime'])
        self.assertTrue(timing_trace(jobs,threshold['critical']-F(1,1000),F(1))[1]['ontime'])
        self.assertFalse(timing_trace(jobs,threshold['critical']+F(1,1000),F(1))[1]['ontime'])

    def test_late_baseline_is_not_repaired_by_relabeling(self):
        jobs=[job('late',0,4,0,4)]
        self.assertFalse(timing_trace(jobs,F(1),F(1))[0]['ontime'])
        self.assertEqual(thresholds(jobs,F(1))[0]['critical'],F(7,8))
        self.assertEqual(thresholds(jobs,F(1,2))[0]['critical'],F(3,8))
        self.assertFalse(timing_trace(jobs,F(2),F(1))[0]['ontime'])

    def test_tightening_is_relative_to_arrival_and_includes_equality(self):
        jobs=[job('shifted',5,2,2,12)]
        q=F(11,20)  # Deadline=2+q*(12-2)=7.5, the response time.
        self.assertTrue(timing_trace(jobs,F(1),q)[0]['ontime'])
        self.assertFalse(timing_trace(jobs,F(1),q-F(1,1000))[0]['ontime'])
        self.assertTrue(timing_trace(jobs,F(1),q+F(1,1000))[0]['ontime'])
        self.assertEqual(thresholds(jobs,q)[0]['critical'],1)

    def test_empty_timing_plan(self):
        self.assertEqual(timing_trace([],F(1),F(1)),[])
        self.assertEqual(thresholds([],F(1)),[])

    def test_brute_suffix_enumeration_agrees_on_varied_chains_and_grid(self):
        # Independently enumerate every possible binding release, summing complete
        # preceding slots directly rather than copying the implementation's recurrence.
        r_grid=list(map(F,['1','1.05','1.1','1.25','1.5','2']))
        q_grid=list(map(F,['1','.9','.8','.5']))
        comparisons=0
        for count in range(1,6):
            jobs=[];cursor=F(0)
            for i in range(count):
                duration=(F(1,2),F(2),F(7,4))[i%3]
                cursor+=F(3,2) if i%2 else F(0)
                arrival=max(F(0),cursor-1)
                slack=(F(-1,4),F(0),F(2),F(10))[i%4]
                jobs.append(job(str(i),cursor,duration,arrival,cursor+duration+F(1,2)+slack))
                cursor+=duration+4
            for q in q_grid:
                limits=thresholds(jobs,q)
                for r in r_grid:
                    rows=timing_trace(jobs,r,q)
                    self.assertEqual([x['id'] for x in rows],[x['id'] for x in jobs])
                    for j,(original,actual,bound) in enumerate(zip(jobs,rows,limits)):
                        expanded=[jobs[k]['t']+sum((F(4)+r*jobs[ell]['d'] for ell in range(k,j)),F(0))+F(1,2)+r*original['d'] for k in range(j+1)]
                        expected=max(expanded)
                        deadline=original['arrival']+q*(original['deadline']-original['arrival'])
                        self.assertEqual(actual['response'],expected)
                        self.assertEqual(actual['ontime'],expected<=deadline)
                        self.assertEqual(actual['ontime'],r<=bound['critical'])
                        self.assertEqual(bound['numerator']/bound['denominator'],bound['critical'])
                        witness=next(k for k in range(j+1) if jobs[k]['id']==bound['witness_id'])
                        at_bound=jobs[witness]['t']+sum((F(4)+bound['critical']*jobs[ell]['d'] for ell in range(witness,j)),F(0))+F(1,2)+bound['critical']*original['d']
                        self.assertEqual(at_bound,deadline)
                        comparisons+=1
        self.assertEqual(comparisons,360)

    def test_each_arm_count_is_monotone_under_separate_stresses(self):
        jobs=[job('a',0,2,0,5),job('b',6,1,1,10),job('c',14,3,8,20)]
        slowdown_counts=[sum(x['ontime'] for x in timing_trace(jobs,r,F(1))) for r in map(F,['1','1.05','1.1','1.25','1.5','2'])]
        deadline_counts=[sum(x['ontime'] for x in timing_trace(jobs,F(1),q)) for q in map(F,['1','.9','.8','.5'])]
        self.assertEqual(slowdown_counts,sorted(slowdown_counts,reverse=True))
        self.assertEqual(deadline_counts,sorted(deadline_counts,reverse=True))


if __name__=='__main__':unittest.main()
