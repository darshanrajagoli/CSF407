# CS F407 — Laboratory: Neural Models (learning, depth, activations, output layers)

A 2–2–1 neural network learns XOR, the "sensors disagree" warning. The lab tests
four things:
- why it needs a nonlinear hidden layer;
- whether backpropagation's gradients are right;
- what goes wrong with identical starting weights;
- how the hidden activation changes learning.

Then the output becomes three classes with softmax. An LLM writes the first
code, and every claim is checked by running it.

```
.
├── INDEX.md                    <- you are here
├── neur_models_lab_ex.pdf      <- the original lab handout
│
├── deliverables/               <- SUBMIT THIS
└── explainers/                 <- for understanding only (LOCAL ONLY, git-ignored)
```

---

## `deliverables/` — what gets submitted

The handout asks for "one notebook or Python file plus a short report" covering
six items. All six are covered.

| # | The lab asks for | Where it is |
|---|---|---|
| 1 | Task 1 problem specification and linear-separability explanation | `LAB_REPORT.md` §1 |
| 2 | Model design and validation criteria (Task 2) | `LAB_REPORT.md` §2 |
| 3 | Exact LLM prompts and the corrections made | `LAB_REPORT.md` §3; prompts and generated code in full in `prompts.md` |
| 4 | Final code for binary XOR and the three-class extension | `neural_xor.py` |
| 5 | Loss, prediction, gradient, symmetry and activation results | `LAB_REPORT.md` §4–§5; raw in `results.txt` |
| 6 | Reflection questions 1–7 | `LAB_REPORT.md` §6 |

All five "Think About It" boxes, and the optional softmax diagnostic, are
answered too.

| File | What it is |
|---|---|
| `LAB_REPORT.md` | **The main document.** One section per task, then the 7 reflection answers |
| `neural_xor.py` | The whole lab in one file: Task 1 check, Task 4 Parts A–D, Task 5 and the diagnostic |
| `prompts.md` | The two prompts, the LLM's code exactly as generated, and what was changed and why |
| `results.txt` | Raw output of `neural_xor.py` |

### Reproducing everything

```bash
cd deliverables
python neural_xor.py      # about 2 minutes on CPU; writes results.txt
```

It needs PyTorch (CPU is enough). It's seeded, so every run prints identical numbers.

---

## `explainers/` — local only, for understanding

This folder is git-ignored. It stays on this computer and is not on GitHub.

| File | What it is |
|---|---|
| `explainer.md` | **Read this first.** Starts from zero (no CS, no maths) and builds to the whole picture. Each section ends with a 📝 notes box, and there's a cheat sheet and likely exam questions at the end |
| `code_walkthrough.md` | `neural_xor.py` explained section by section, in plain English |

---

## The three things worth knowing

**1. It's the nonlinearity, not the depth.** A linear model, and a 2–2–1 network
with *no* activation, both end at probability 0.5 on every input: loss ln 2, 2/4
correct. With tanh added, the same shape gets 4/4 and loss 0.0002. The two hidden
units become "only sensor 2 on" and "only sensor 1 on" detectors. Nobody told
them to.

**2. The LLM's code looked right and passed its own tests, but failed 11 times
out of 20.** On seed 0 it solved XOR. Across 20 seeds only 9 did. Its "final
loss" was also from before the last update, and its gradient check looked at
the one moment the gradient *should* be zero. Only reading the code against
the design, and running it across seeds, showed this.

**3. Identical starts never separate.** With every weight equal, the two hidden
units stay equal at every step and act as one unit, stuck at 3/4. With every
weight at zero it is worse: every gradient is exactly zero (hidden outputs
tanh(0) = 0, output weights 0, and XOR's two-and-two labels cancel the output
bias's error), so nothing moves at all. Random initialisation is what breaks the tie.
