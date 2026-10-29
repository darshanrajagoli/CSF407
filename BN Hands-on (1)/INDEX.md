# CS F407 — BN: Hands-on (1)

**Quanta Week 6:** [BN: Hands-on (1)](https://quanta.bits-pilani.ac.in/mod/url/view.php?id=5364).
**Topic:** Building and Learning a Bayesian Network.

This is the Cloudy/Rain/Sprinkler/WetGrass practical. The separate
[Week 8 BN lab](../BN%20Hands-on/INDEX.md) covers autoregressive language models.

Start with [the report](deliverables/LAB_REPORT.md).

| File | Purpose |
|---|---|
| [Report](deliverables/LAB_REPORT.md) | Model, inference, estimation, exercises and explanations |
| [sprinkler.py](deliverables/sprinkler.py) | Complete practical, including homework and classroom experiments |
| [test_sprinkler.py](deliverables/test_sprinkler.py) | Independent checks of probabilities, learning and validation |
| [results.txt](deliverables/results.txt) | Captured results, including reference and learned CPTs |
| [test_results.txt](deliverables/test_results.txt) | Captured test results |
| [requirements.txt](deliverables/requirements.txt) | Tested package versions |
| [sample_size.png](deliverables/sample_size.png) | Parameter estimate versus sample size |
| [Supplied notebook](source/building_and_learning_bn.ipynb) | Unmodified course reference supplied in this chat; its saved outputs are reference material |

## Run

From the repository root:

```bash
python -m pip install -r "BN Hands-on (1)/deliverables/requirements.txt"
python "BN Hands-on (1)/deliverables/sprinkler.py"
python "BN Hands-on (1)/deliverables/test_sprinkler.py"
```

The first command installs the dependencies. The practical runs locally without
model downloads. The report focuses on the mathematical model, implementation
and results; development-process reflection is reserved for the author's later
addition.

[Back to course index](../INDEX.md)
