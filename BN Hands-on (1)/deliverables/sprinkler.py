"""Week 6: build, query, learn and check the Sprinkler Bayesian network.

Run: python sprinkler.py
Install dependencies first: python -m pip install -r requirements.txt
"""
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
import pgmpy
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from pgmpy.parameter_estimator import DiscreteMLE, DiscreteBayesianEstimator

EDGES = [("Cloudy", "Rain"), ("Cloudy", "Sprinkler"),
         ("Rain", "WetGrass"), ("Sprinkler", "WetGrass")]
NODES = ["Cloudy", "Rain", "Sprinkler", "WetGrass"]
STATES = {node: [0, 1] for node in NODES}


def build_model():
    """State 0 means false; state 1 means true."""
    model = DiscreteBayesianNetwork(EDGES)
    model.add_cpds(
        TabularCPD("Cloudy", 2, [[0.5], [0.5]]),
        TabularCPD("Rain", 2, [[0.8, 0.2], [0.2, 0.8]],
                   evidence=["Cloudy"], evidence_card=[2]),
        TabularCPD("Sprinkler", 2, [[0.5, 0.9], [0.5, 0.1]],
                   evidence=["Cloudy"], evidence_card=[2]),
        # Columns: (Rain,Sprinkler) = (0,0), (0,1), (1,0), (1,1).
        TabularCPD("WetGrass", 2,
                   [[0.99, 0.10, 0.10, 0.01], [0.01, 0.90, 0.90, 0.99]],
                   evidence=["Rain", "Sprinkler"], evidence_card=[2, 2]),
    )
    model.check_model()
    return model


def joint(c, r, s, w):
    """Independent mathematical specification, not a read of library CPDs."""
    rain = 0.8 if c else 0.2
    sprinkler = 0.1 if c else 0.5
    wet = {(0, 0): 0.01, (0, 1): 0.90,
           (1, 0): 0.90, (1, 1): 0.99}[r, s]
    return (0.5 * (rain if r else 1-rain)
            * (sprinkler if s else 1-sprinkler) * (wet if w else 1-wet))


def enumerate_probability(query, evidence):
    """P(query=1 | evidence), by summing the 16 possible assignments."""
    numerator = denominator = 0.0
    for values in itertools.product([0, 1], repeat=4):
        assignment = dict(zip(NODES, values))
        if all(assignment[node] == value for node, value in evidence.items()):
            probability = joint(*values)
            denominator += probability
            if assignment[query] == 1:
                numerator += probability
    return numerator / denominator


def query_probability(model, query, evidence):
    result = VariableElimination(model).query(
        [query], evidence=evidence, show_progress=False)
    return float(result.get_value(**{query: 1}))


def sample_data(n, seed):
    """Ancestral sampling: C first, then R and S, then W."""
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        c = int(rng.random() < 0.5)
        r = int(rng.random() < (0.8 if c else 0.2))
        s = int(rng.random() < (0.1 if c else 0.5))
        wet = {(0, 0): 0.01, (0, 1): 0.90,
               (1, 0): 0.90, (1, 1): 0.99}[r, s]
        w = int(rng.random() < wet)
        rows.append((c, r, s, w))
    return pd.DataFrame(rows, columns=NODES)


def fit_model(data, bayesian=False):
    """Keep the graph fixed; estimate its CPTs using binary state names."""
    model = DiscreteBayesianNetwork(EDGES)
    estimator = (DiscreteBayesianEstimator(state_names=STATES, prior_type="BDeu",
                                            equivalent_sample_size=10)
                 if bayesian else DiscreteMLE(state_names=STATES))
    model.fit(data, estimator=estimator)
    model.check_model()
    return model


def rain_given_cloudy(model):
    return float(model.get_cpds("Rain").get_value(Rain=1, Cloudy=1))


def change_wet_cpd(model, true_probabilities):
    """Replace one CPT to demonstrate validation failures."""
    model.remove_cpds(model.get_cpds("WetGrass"))
    model.add_cpds(TabularCPD(
        "WetGrass", 2,
        [[1-p for p in true_probabilities], true_probabilities],
        evidence=["Rain", "Sprinkler"], evidence_card=[2, 2]))
    return model


def cpt_rows(model):
    """Print every parent configuration; avoid truncated library tables."""
    rows = []
    for node in NODES:
        cpd = model.get_cpds(node)
        parents = cpd.variables[1:]
        for values in itertools.product([0, 1], repeat=len(parents)):
            evidence = dict(zip(parents, values))
            probability = float(cpd.get_value(**{node: 1, **evidence}))
            rows.append(f"P({node}=1 | {evidence}) = {probability:.12f}")
    return rows


def main():
    lines = []

    def out(text=""):
        print(text)
        lines.append(str(text))

    model = build_model()
    out(f"Versions: pgmpy={pgmpy.__version__}, numpy={np.__version__}, pandas={pd.__version__}")
    out("Graph: Cloudy -> Rain; Cloudy -> Sprinkler; Rain,Sprinkler -> WetGrass")
    out("All states: 0=False, 1=True. Model valid: " + str(model.check_model()))
    for row in cpt_rows(model):
        out(row)

    out("\nINFERENCE: library result / independent enumeration")
    cases = [("Rain", {}), ("Sprinkler", {}), ("Cloudy", {}),
             ("Rain", {"WetGrass": 1}), ("Sprinkler", {"WetGrass": 1}),
             ("Cloudy", {"WetGrass": 1}),
             ("Rain", {"WetGrass": 1, "Sprinkler": 0})]
    for variable, evidence in cases:
        value = query_probability(model, variable, evidence)
        expected = enumerate_probability(variable, evidence)
        assert np.isclose(value, expected, atol=1e-12, rtol=0)
        out(f"P({variable}=1 | {evidence}) = {value:.12f} / {expected:.12f}")

    data = sample_data(1000, 7)
    mle = fit_model(data)
    cloudy = data[data.Cloudy == 1]
    manual = float((cloudy.Rain == 1).mean())
    out(f"\nMLE N=1000 seed=7: Rain=1,Cloudy=1 count={int(cloudy.Rain.sum())}; Cloudy=1 count={len(cloudy)}")
    out(f"Manual P(Rain=1 | Cloudy=1)={manual:.12f}; pgmpy={rain_given_cloudy(mle):.12f}")
    assert np.isclose(manual, rain_given_cloudy(mle))
    out("Learned MLE CPTs, N=1000:")
    for row in cpt_rows(mle):
        out(row)

    out("\nSAMPLE SIZE: N / Rain given Cloudy estimate / absolute error from 0.8")
    sizes = [20, 50, 100, 500, 1000, 5000]
    estimates = []
    for n in sizes:
        estimate = rain_given_cloudy(fit_model(sample_data(n, 7)))
        estimates.append(estimate)
        out(f"{n}: {estimate:.6f}; error={abs(estimate-0.8):.6f}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(sizes, estimates, marker="o", label="MLE, seed 7")
    ax.axhline(0.8, linestyle="--", color="black", label="True value: 0.8")
    ax.set(xscale="log", xlabel="Number of observations",
           ylabel="P(Rain=1 | Cloudy=1)", title="Parameter estimate versus sample size")
    ax.legend()
    fig.tight_layout()
    fig.savefig(Path(__file__).with_name("sample_size.png"), dpi=160)
    plt.close(fig)

    out("\nSPARSE DATA: N=30 seed=11; same data for both estimators")
    small = sample_data(30, 11)
    for name, bayesian in [("MLE", False), ("BDeu ESS=10", True)]:
        fitted = fit_model(small, bayesian)
        out(f"{name}: P(Rain=1 | Cloudy=1)={rain_given_cloudy(fitted):.6f}")
        for row in cpt_rows(fitted):
            out(row)

    out("\nDIFFERENT DATASETS: N=100 / seed / Rain given Cloudy estimate")
    for seed in [1, 2, 3, 4, 5]:
        out(f"seed={seed}: {rain_given_cloudy(fit_model(sample_data(100, seed))):.6f}")

    out("\nVALIDATION FAILURES")
    broken = build_model()
    broken.get_cpds("Rain").values[0, 0] = 0.9
    broken.get_cpds("Rain").values[1, 0] = 0.3
    try:
        broken.check_model()
    except ValueError:
        out("Non-normalized CPT (column sum 1.2): rejected, as expected.")
    else:
        raise AssertionError("Invalid CPT accepted")
    wrong = change_wet_cpd(build_model(), [0.01, 0.90, 0.99, 0.90])
    out(f"Wrong parent-state columns: check_model()={wrong.check_model()}")
    out(f"Wrong P(Rain=1 | WetGrass=1)={query_probability(wrong, 'Rain', {'WetGrass': 1}):.12f}")
    out("Normalization alone cannot detect a semantically wrong CPT.")
    Path(__file__).with_name("results.txt").write_text("\n".join(lines)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
