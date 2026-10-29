"""Check mathematical results and estimation, including misleading valid CPTs."""
import itertools
import unittest
import numpy as np
from sprinkler import (NODES, EDGES, build_model, joint, enumerate_probability,
                       query_probability, sample_data, fit_model,
                       rain_given_cloudy, change_wet_cpd)


class SprinklerTests(unittest.TestCase):
    def test_structure_and_all_joint_assignments(self):
        model = build_model()
        self.assertEqual(set(model.edges()), set(EDGES))
        self.assertTrue(model.check_model())
        total = 0
        for values in itertools.product([0, 1], repeat=4):
            assignment = dict(zip(NODES, values))
            probability = 1
            for node in NODES:
                cpd = model.get_cpds(node)
                probability *= cpd.get_value(**{v: assignment[v] for v in cpd.variables})
            self.assertAlmostEqual(probability, joint(*values), places=12)
            total += probability
        self.assertAlmostEqual(total, 1)

    def test_all_homework_queries(self):
        model = build_model()
        for variable, evidence, expected in [
            ("Rain", {"WetGrass": 1}, 0.7047692307692307),
            ("Sprinkler", {"WetGrass": 1}, 0.4278461538461539),
            ("Cloudy", {"WetGrass": 1}, 0.5746153846153845),
            ("Rain", {"WetGrass": 1, "Sprinkler": 0}, 0.9922022048937886),
        ]:
            with self.subTest(variable=variable, evidence=evidence):
                self.assertAlmostEqual(query_probability(model, variable, evidence), expected)
                self.assertAlmostEqual(enumerate_probability(variable, evidence), expected)

    def test_mle_matches_counts_and_keeps_graph(self):
        data = sample_data(1000, 7)
        model = fit_model(data)
        self.assertEqual(set(model.edges()), set(EDGES))
        subset = data[data.Cloudy == 1]
        self.assertAlmostEqual(rain_given_cloudy(model), subset.Rain.mean())

    def test_bdeu_matches_pseudocount_formula(self):
        data = sample_data(30, 11)
        subset = data[data.Cloudy == 1]
        # Rain has 2 states and 2 parent configurations: 10/4 per cell.
        expected = (subset.Rain.sum() + 2.5) / (len(subset) + 5)
        self.assertAlmostEqual(rain_given_cloudy(fit_model(data, True)), expected)

    def test_binary_states_with_sparse_data(self):
        data = sample_data(1, 7)
        for bayesian in [False, True]:
            model = fit_model(data, bayesian)
            self.assertTrue(model.check_model())
            for cpd in model.get_cpds():
                self.assertEqual(cpd.variable_card, 2)
                self.assertTrue(np.allclose(cpd.get_values().sum(axis=0), 1))

    def test_invalid_normalization_is_rejected(self):
        model = build_model()
        model.get_cpds("Rain").values[:, 0] = [0.9, 0.3]
        with self.assertRaises(ValueError):
            model.check_model()

    def test_wrong_semantics_needs_more_than_normalization(self):
        wrong = change_wet_cpd(build_model(), [0.01, 0.90, 0.99, 0.90])
        self.assertTrue(wrong.check_model())
        value = query_probability(wrong, "Rain", {"WetGrass": 1})
        self.assertAlmostEqual(value, 0.7172952268709487)
        self.assertNotAlmostEqual(value, enumerate_probability("Rain", {"WetGrass": 1}))

    def test_data_reproducibility(self):
        self.assertTrue(sample_data(100, 7).equals(sample_data(100, 7)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
