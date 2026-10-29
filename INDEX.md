# CS F407 — Artificial Intelligence

Coursework organized using the names and order in Quanta. Week numbers below
come from the course outline; they are not invented lab numbers.

## Quanta course map

| Week | Quanta resources | Work in this repository |
|---|---|---|
| 1 | Introduction; Neural Models: Lecture 1, Lecture 2, Hands-on | [Neural Models Hands-on](Neural%20Models%20Hands-on/INDEX.md) |
| 2 | Agents: Lecture, Hands-on; LLMs: Lecture | [Agents Hands-on](Agents%20Hands-on/INDEX.md) |
| 3 | Search: Lecture, Hands-on | [Search Hands-on](Search%20Hands-on/INDEX.md) |
| 4 | Logic: Lecture, Hands-on | [Logic Hands-on](Logic%20Hands-on/INDEX.md), including the 28 October locked-door domain |
| 5 | AR Models: Lecture (1), Lecture (2) | Related autoregressive-model work is in [BN Hands-on](BN%20Hands-on/INDEX.md) |
| 6 | Probability: Intro; BN: Lecture; BN: Hands-on (1) | [BN: Hands-on (1)](BN%20Hands-on%20%281%29/INDEX.md): building and learning the Sprinkler network |
| 7 | AR Models: Hands-on; RAG: Lecture (1), Lecture (2) | Related n-gram work is in [BN Hands-on](BN%20Hands-on/INDEX.md); no separate RAG deliverable is present |
| 8 | BN: Lab | [BN Hands-on](BN%20Hands-on/INDEX.md): supplied BN lab handout, code and report |
| 9–11 | No resources listed in the pasted outline | No additional resource mapping established |

The outline gives resource titles, not the contents of its linked documents.
Week 6 is mapped to the supplied Building and Learning a Bayesian Network
notebook. The separate Week 7 AR Models hands-on resource has not been compared
against its original contents, so this index does not certify its separate
completion. Related autoregressive work remains in the Week 8 BN lab.

## Neural Models: Hands-on — Week 1

A small neural network learns XOR. The work covers depth, backpropagation,
symmetry, sigmoid/tanh/ReLU and a three-class softmax output.

- [Folder index](Neural%20Models%20Hands-on/INDEX.md)
- [Report](Neural%20Models%20Hands-on/deliverables/LAB_REPORT.md)
- [Code](Neural%20Models%20Hands-on/deliverables/neural_xor.py)
- [Handout](Neural%20Models%20Hands-on/neur_models_lab_ex.pdf)

## Agents: Hands-on — Week 2

A standalone goal-based warehouse agent using BFS on the Agents handout's exact
map. The verified shortest path is 20 moves. Covers problem understanding,
scaling, architecture, algorithm explanation and execution checks. Personal
process reflection is reserved for Darshan's final addition.

- [Folder index](Agents%20Hands-on/INDEX.md)
- [Report](Agents%20Hands-on/deliverables/LAB_REPORT.md)
- [Code](Agents%20Hands-on/deliverables/agents.py)
- [Handout](Agents%20Hands-on/agents_lab.pdf)

## Search: Hands-on — Week 3

Warehouse search using A*, BFS, heuristic comparisons and correctness tests.
This uses a different warehouse from the Agents handout.

- [Folder index](Search%20Hands-on/INDEX.md)
- [Report](Search%20Hands-on/deliverables/LAB_REPORT.md)
- [Code](Search%20Hands-on/deliverables/astar_warehouse.py)
- [Handout](Search%20Hands-on/search_lab_ex.pdf)

## Logic: Hands-on — Week 4

Package-delivery planning using logical preconditions/effects and BFS, with
Prolog verification. Includes the second domain transcribed in class on
28 October 2026: collect the key, unlock the door and reach room C.

- [Folder index](Logic%20Hands-on/INDEX.md)
- [Report](Logic%20Hands-on/deliverables/LAB_REPORT.md)
- [Locked-door navigation](Logic%20Hands-on/2026-10-28%20Locked-Door%20Navigation/README.md)
- [Handout](Logic%20Hands-on/logic_lab_ex.pdf)

## BN: Hands-on (1) — Week 6

Build the Cloudy/Rain/Sprinkler/WetGrass network, perform exact inference, learn
CPTs from data using MLE and BDeu, and validate the model. Includes the homework
queries, CPT interpretation, sample-size plot and different-seed exercise.

- [Folder index](BN%20Hands-on%20%281%29/INDEX.md)
- [Report](BN%20Hands-on%20%281%29/deliverables/LAB_REPORT.md)
- [Code](BN%20Hands-on%20%281%29/deliverables/sprinkler.py)
- [Supplied course notebook](BN%20Hands-on%20%281%29/source/building_and_learning_bn.ipynb)

## BN: Lab — Week 8; related BN / AR Models work

First-order and second-order autoregressive language models viewed as Bayesian
networks. Includes conditional probability tables, generation, probability
checks and the supplied handout's questions/reflection.

- [Folder index](BN%20Hands-on/INDEX.md)
- [Report](BN%20Hands-on/deliverables/LAB_REPORT.md)
- [First-order code](BN%20Hands-on/deliverables/bigram_model.py)
- [Second-order code](BN%20Hands-on/deliverables/trigram_model.py)
- [Handout](BN%20Hands-on/bn_lab_ex.pdf)

This folder was previously named `Bayesian Networks Hands-on`; it is now
`BN Hands-on` to follow Quanta's label.

## Additional work — Transformer architectures

The [Machine Translation Hands-on folder](Machine%20Translation%20Hands-on/INDEX.md)
contains [a notebook](Machine%20Translation%20Hands-on/deliverables/transformer_architectures_demo.ipynb)
with encoder–decoder translation, decoder-only generation and encoder-only
sentiment examples. Its exact Quanta resource association is unverified, so it
is listed separately rather than assigned a course week.

## Repository layout and study material

Each lab has an `INDEX.md`, a `deliverables/` folder and its original PDF when
available. Existing `explainers/` folders contain local study notes and are
Git-ignored. The new Agents lab keeps its explanation in the report.

The [course handout](ai_handout_2026-2027_s1.pdf) is at the repository root.
The term project, [whospoke](https://github.com/darshanrajagoli/whospoke), has its
own repository; the local `project/` checkout is excluded from this repository.

## Run checks

From this repository's root:

```bash
python "Agents Hands-on/deliverables/agents.py"
python "Agents Hands-on/deliverables/test_agents.py"
python "Search Hands-on/deliverables/test_search.py"
python "Logic Hands-on/deliverables/test_planner.py"
python "Logic Hands-on/deliverables/run_prolog.py"
python "Logic Hands-on/2026-10-28 Locked-Door Navigation/locked_door.py"
python "BN Hands-on (1)/deliverables/test_sprinkler.py"
python "BN Hands-on/deliverables/test_models.py"
python "Neural Models Hands-on/deliverables/neural_xor.py"
```

The neural program requires PyTorch. The Transformer notebook documents its
own dependencies. The Week 6 BN practical has its own pinned requirements
file. Other listed checks use the Python standard library.
