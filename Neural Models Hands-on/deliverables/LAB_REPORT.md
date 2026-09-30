# Lab Report: Neural Models (learning, depth, activations and output layers)

**CS F407 Artificial Intelligence**

Every number here comes from `neural_xor.py`, except the LLM-draft and
optimiser-sweep numbers in §3, which come from running the LLM's own code
(`prompts.md`). The script prints everything and saves it to `results.txt`. It is
seeded, so every run prints the same numbers.

```bash
python neural_xor.py      # CPU, about 2 minutes. Needs PyTorch.
```

### The six submission items

| # | Asked for | Where |
|---|---|---|
| 1 | Task 1 problem specification and linear-separability explanation | §1 |
| 2 | Model design and validation criteria (Task 2) | §2 |
| 3 | The exact LLM prompts and the corrections made | §3; prompts and generated code in full in `prompts.md` |
| 4 | Final code for binary XOR and the three-class extension | `neural_xor.py` (one file) |
| 5 | Loss, prediction, gradient, symmetry and activation results | §4, §5; raw output in `results.txt` |
| 6 | Reflection questions 1–7 | §6 |

Each "Think About It" box is answered at the end of the task it belongs to.

---

## 1. Task 1: Understand the problem before coding

**Specification.**
- Input space: 𝒳 = {0,1}², the two sensor readings (x₁, x₂).
- Output space: 𝒴 = {0,1}, where 1 = raise the disagreement warning.
- The four labelled examples:

| x₁ | x₂ | y |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

The agent must compute P(y = 1 | x₁, x₂) and warn when it is above 0.5.

**Sketch.** `1` = warning, `0` = no warning.

```
 x2
  1 |  1 (0,1)      0 (1,1)
    |
  0 |  0 (0,0)      1 (1,0)
    +--------------------------- x1
       0            1
```

**Why one straight line can't separate the classes.** The two 1s sit on one
diagonal and the two 0s on the other. A straight line that puts both 1s on one
side must also put at least one 0 on that side, so any line misclassifies at
least one point. Formally, w₁x₁ + w₂x₂ + b > 0 would be needed for (0,1) and (1,0).
Adding those two gives w₁ + w₂ + 2b > 0. But ≤ 0 is needed for (0,0) and (1,1),
and adding those gives w₁ + w₂ + 2b ≤ 0. That is a contradiction.

**Prediction for one affine map + sigmoid.** It can't get all four right. The
best it can do on balanced data is hedge. By symmetry, the loss is minimised by
predicting 0.5 everywhere, with loss ln 2 ≈ 0.693.

**Result:** loss 0.6931 and all four probabilities exactly 0.5000, so 2/4 correct.
A 2–2–1 network with **no** hidden activation gets the same result: 0.6931, all
0.5, 2/4. Stacked affine layers are still one affine map.

**Think About It: what claim about representation does XOR test with four points?**
It tests the claim that a model's **kind of representation** matters, not its
size. A linear model can have any number of parameters and still fail, because
every function it can express has a straight-line boundary. XOR asks whether
the model can build an internal representation in which the problem *becomes*
linearly separable. Four points are enough because there is no noise and no
generalisation question. Success or failure is purely about representation.

---

## 2. Task 2: Design (written before prompting)

**Model:**
- 2 inputs → 2 hidden units → 1 output logit;
- hidden activation **tanh** (sigmoid and ReLU compared in Task 4D);
- output: one logit, turned into a probability by a sigmoid, via
  `BCEWithLogitsLoss`;
- loss: binary cross-entropy, averaged over the 4 examples;
- optimisation: full-batch gradient descent, 3000 steps, seed 0.

**Q1. Why is the hidden nonlinearity scientifically necessary?**
Without it, W₂(W₁x + b₁) + b₂ = W′x + b′ is one affine map, and §1 shows no
affine map separates XOR. The nonlinearity lets each hidden unit bend its input
space. The output layer then draws a straight line in the *hidden* space, where
the classes can be separated.

**Q2. Why is sigmoid + binary cross-entropy a sensible output pairing?**
- The sigmoid turns a logit into a probability between 0 and 1, which is what a
  yes/no answer needs.
- Binary cross-entropy is the negative log-likelihood of that probability, so
  training maximises the probability of the correct labels.
- Together the gradient with respect to the logit is just **p − y**. It never
  vanishes while the prediction is wrong.
- `BCEWithLogitsLoss` computes both in one numerically stable step.

**Q3. Validation criteria (what counts as successful learning):**

1. the final loss is below 0.01;
2. all four thresholded predictions equal the targets;
3. the first-layer gradient at the start is non-zero **and** matches a
   finite-difference estimate;
4. the result is checked over several seeds (20), and the failure rate is
   reported, not hidden.

**Think About It: the hidden units have no targets. What decides what they compute?**
The output loss does, through backpropagation. The chain rule passes each hidden
unit its share of the output error: δ_hidden = (W₂ᵀ δ_out) ⊙ f′(a). Each unit is
pushed towards whatever feature most reduces the loss. Random initialisation
makes the two units start differently, so they end up different. In our run,
**unit 1 fires only for (0,1) and unit 2 fires only for (1,0).** These are "x₂ and
not x₁" and "x₁ and not x₂". The output then says "yes if either unit fires".
Nobody specified those features. Backpropagation found them.

---

## 3. Task 3: Using the LLM for a first implementation

The exact prompt and the generated code are in `prompts.md`. Before running, the
four places the handout asks about were found: forward pass `model(X)`, scalar loss
`loss_fn(logits, y)`, reverse-mode AD `loss.backward()`, and parameter update
`optimizer.step()`.

**Two changes made before running:**
1. The printed "final loss" came from *before* the last update, so it was
   recomputed after training.
2. The gradient test used the *last* step's gradient, which is near zero when
   training works. It was replaced by the gradient at the start, checked against
   finite differences.

**One change made after running:** only 9 of 20 seeds (0–19) learned XOR with
the LLM's Adam (lr 0.05). On a 50-seed sweep, switching to SGD with momentum 0.9
and lr 0.5 raised the success rate from 27/50 to 41/50 (on seeds 0–19: 9/20 →
14/20). This is an engineering setting; the model and task are unchanged.

**Think About It: what can be checked from the code without running it, and what can't?**

- **From the code alone:**
  - the architecture (2–2–1), the activation, and the data;
  - that one logit goes into `BCEWithLogitsLoss`, so no sigmoid is applied twice;
  - that `zero_grad()` comes before `backward()` and `step()` after;
  - that the loss is a mean and a seed is set.

  These are properties of *what* the program computes.
- **Only by running it:**
  - whether it actually learns, or stops in a local minimum;
  - how often that happens across seeds;
  - how large the gradients are, and whether they're numerically right;
  - whether symmetric weights stay symmetric;
  - how the activations compare.

  These are properties of *what happens*. The LLM's code looked right and
  passed its own tests on seed 0, yet failed on 11 of 20 seeds.

---

## 4. Task 4: Execute, test and diagnose

### Part A: Basic learning check (tanh, seed 0)

| | Value |
|---|---|
| Initial loss | 0.7152 |
| Final loss | 0.000206 |

| x | P(warning) | Label | Target |
|---|---|---|---|
| (0,0) | 0.0001 | 0 | 0 |
| (0,1) | 0.9997 | 1 | 1 |
| (1,0) | 0.9997 | 1 | 1 |
| (1,1) | 0.0001 | 0 | 0 |

**All four are correct.** The only setting changed from the LLM's version was the
optimiser (§3). That is an engineering setting, and the task is unchanged.

### Part B: Backpropagation check

The gradient dL/dW⁽¹⁾ at the start of training:

| | from x₁ | from x₂ |
|---|---|---|
| hidden unit 1 | 0.0005 | 0.0006 |
| hidden unit 2 | −0.0426 | −0.0448 |

**What `parameter.grad` means:** entry (i, j) of `net[0].weight.grad` is ∂L/∂W⁽¹⁾ᵢⱼ.
It says how fast the loss changes if the weight from input j to hidden unit i is
nudged. Its sign says which way to move the weight to lower the loss.
`backward()` computes all these entries in one pass, by the chain rule.

**Why a mean loss gives the mean of the example gradients:**
L = ¼ Σᵢ Lᵢ, and differentiation is linear, so ∂L/∂W = ¼ Σᵢ ∂Lᵢ/∂W. The measured
difference between the two is 0.0 (exactly equal).

**Checks that the gradient is right and useful:**
- **Correct:** a finite-difference estimate, (L(w+ε) − L(w−ε)) / 2ε with
  ε = 10⁻⁶, computed on a float64 copy of the network, matches `backward()` to
  within 3.7×10⁻⁹ (largest relative difference 2.2×10⁻⁷, so even the small
  unit-1 entries are confirmed). float64 is used because in float32 the rounding
  error of the loss, divided by 2ε, would be as large as those small entries.
- **Useful:** one small step against the gradient lowers the loss (0.71516 →
  0.71504).
- **After training:** the largest entry is 1.3×10⁻⁵. It is near zero because
  the loss is near its minimum.

### Part C: Symmetry experiment (tanh, same architecture)

| Start | Rows of W⁽¹⁾ during training | After 3000 steps |
|---|---|---|
| every weight and bias = 0 (the handout's case) | largest gradient at step 0 is exactly 0; both rows stay [0, 0] at steps 0, 1, 10, 100 and 2999 | P = 0.5 everywhere, 2/4 correct, loss 0.6931 |
| every weight and bias = 0.5 | largest gradient at step 0 is 0.27; rows change (0.50 → 0.43 → 3.48 → 5.72) but are **identical at every step** | 3/4 correct, loss 0.4775 |

**Why the rows stay identical.** If both hidden units start with the same weights:
- they compute the same output for every input;
- they connect to the output through equal weights, so they receive the same
  error signal;
- so they get the same gradient and the same update.

By induction they stay identical forever, and the network acts as if it had
**one** hidden unit. One unit can't represent XOR, so it gets stuck at 3/4.

**Why the all-zero case doesn't move at all.** With every parameter at zero, each
hidden unit outputs tanh(0) = 0 for every input, and the prediction is 0.5
everywhere. The gradient for W⁽²⁾ is then (p − y) × h, where h = 0, so it is
zero. The gradients for W⁽¹⁾ and b⁽¹⁾ pass back through W⁽²⁾ = 0, so they are
zero too. (These three would be zero for *any* labels.) The output bias gets
the average of (0.5 − y), which is 0 because XOR has two 1s and two 0s. So every
gradient is exactly zero (measured: 0.0) and nothing ever changes. This is a
stationary point, a stronger failure than symmetry alone. **Random
initialisation is what breaks the tie.**

### Part D: Activation experiment (same starting weights, seed 0)

| Hidden activation | Final loss | 4/4 correct? | Early ‖∇_W⁽¹⁾ L‖₂ (step 0) | Seeds solved (of 20) |
|---|---|---|---|---|
| Sigmoid | 0.001391 | yes | 0.0009 | 15/20 |
| Tanh | 0.000206 | yes | 0.0618 | 14/20 |
| ReLU | 0.477386 | no (3/4) | 0.0017 | 3/20 |

**Interpretation.** These results are for this experiment only. Four points and
two hidden units can't show that one activation is "best" in general.

With the same starting weights:
- **Tanh** starts with a gradient about 70× larger than sigmoid's. Two measured
  effects explain the gap:
  1. **Derivative size.** Sigmoid's derivative is at most 0.25 (here 0.20–0.25),
     while tanh's reaches up to 1 (here 0.48–0.99). So each example's own
     gradient is about 3× smaller: 0.0524 against 0.1755.
  2. **Cancellation.** At the start the sigmoid network outputs almost the same
     probability for all four inputs (0.52–0.56). Each first-layer weight is
     affected only by the examples where its input is 1: one "warn" example
     ((0,1) or (1,0), error p − 1 ≈ −0.46) and the "no warn" example (1,1)
     (error p ≈ +0.52). With near-equal outputs these two pushes are nearly
     equal and opposite, and (0,0) adds nothing (its inputs are 0). The mean
     gradient is 59× smaller than a single example's. Tanh's starting outputs
     vary more (0.38–0.51), so they cancel only 3×. (Cancellation factor =
     average of the four per-example gradient norms ÷ norm of the mean gradient.)
- **Both still solve seed 0,** and over 20 seeds they're about equally reliable:
  15 and 14.
- **ReLU** failed on seed 0. At the start, only 3 of 8 (input, unit) pairs had a
  positive pre-activation. The others have derivative exactly 0. After
  training, **one of the two units is dead**: negative on all four inputs, so
  its output and gradient are exactly zero. The network is left with one
  working unit and gets stuck at 3/4 with loss 0.4774, almost exactly the
  symmetric network's 0.4775 in Part C (both are, in effect, one hidden
  unit). With only two hidden units, losing one is fatal. ReLU solved 3 of 20
  seeds.

**Think About It: a saturated sigmoid and a dead ReLU both give small gradients.
How can you tell them apart?** Look at the pre-activations a = W⁽¹⁾x + b⁽¹⁾:
- **Saturated sigmoid:** |a| is large (say above 5), the outputs sit near 0 or 1,
  and the derivative is *small but not zero*. It still changes a little with
  the input.
- **Dead ReLU:** a ≤ 0 for *every* input, so the output is *exactly 0* and the
  derivative is *exactly 0*. No signal gets through at all.

Our run shows why you need to look. Sigmoid's small gradient was **neither**: its
derivative was 0.20–0.25, close to its maximum, so not saturated. The smallness
came from examples cancelling. ReLU's failure really was a dead unit (1/2).

---

## 5. Task 5: Three-class output

**Predicted before accepting the LLM's change** (`prompts.md`, Prompt 2):

1. **Final weight matrix shape:** 3 × 2, one row per class and one column per
   hidden unit. Measured: `(3, 2)`. ✓
2. **Logits per example:** 3. Measured: 3. ✓
3. **Why softmax probabilities sum to one:** pᵢ = e^{zᵢ} / Σⱼ e^{zⱼ}. Every term is
   positive, and the numerators add up to exactly the denominator. Measured for
   x = (0,1): 1.0000000. ✓
4. **Why the logit gradient is p − y:** L = −log p_y = −z_y + log Σⱼ e^{zⱼ}.
   Differentiating: ∂L/∂zₖ = −[k = y] + e^{zₖ}/Σⱼ e^{zⱼ} = pₖ − yₖ, where y is
   one-hot. Measured at the start of training (summed loss, so no ¼ factor): the
   gradient from `backward()` and p − y differ by at most 3.0×10⁻⁸. For
   x = (0,1) both are [0.2395, −0.6698, 0.4303]. ✓ (With the default *mean*
   loss it is (p − y)/4.)

**Results** (tanh, 2 hidden units, `CrossEntropyLoss`): initial loss 1.0591
(chance level is ln 3 = 1.0986), final loss 0.000109, **4/4 correct**.

| x | P(class 0) | P(class 1) | P(class 2) | Predicted |
|---|---|---|---|---|
| (0,0) | 0.9999 | 0.0001 | 0.0000 | 0 |
| (0,1) | 0.0000 | 0.9999 | 0.0001 | 1 |
| (1,0) | 0.0000 | 0.9999 | 0.0001 | 1 |
| (1,1) | 0.0000 | 0.0001 | 0.9999 | 2 |

**Why p − y matters:** the error signal is simply "what you predicted minus what
was right". It is large when the model is confidently wrong and zero when it is
exactly right. It is the multi-class version of the binary p − y in §2.

**Diagnostic (the handout marks it optional; done anyway).** Add 100 to all three
logits:
- `softmax(z + 100)` equals `softmax(z)` to within 1.5×10⁻¹⁰, because the e¹⁰⁰
  factor cancels between numerator and denominator.
- **Computed naively in float32, it breaks:** e^{z+100} overflows to `inf`, and
  inf/inf gives `nan, nan, nan`.
- Subtracting the largest logit first gives the right answer. Because of the
  cancellation, that subtraction doesn't change the result, and it keeps the
  biggest exponent at e⁰ = 1, so nothing can overflow. That is why stable
  implementations, including PyTorch's `softmax` and `CrossEntropyLoss`, always
  subtract the maximum first.

**Think About It: next-token prediction is classification over tens of
thousands of words. What stays the same, and what changes?**
- **Stays the same:**
  - softmax over the logits;
  - cross-entropy as the loss;
  - the p − y gradient;
  - probabilities summing to 1;
  - subtracting the maximum for stability;
  - picking a class by argmax or by sampling.

  This is the same P(next token | context) seen in the Bayesian Networks lab.
- **Changes dramatically:**
  - the output matrix goes from 3 × 2 to vocabulary × hidden size, which is
    millions of weights;
  - computing the softmax denominator over the whole vocabulary becomes a real
    cost;
  - the 2-unit hidden layer becomes a deep network that reads a whole sequence
    of tokens (for example, a transformer with attention);
  - training needs vastly more data and compute;
  - generating text needs a decoding strategy.

---

## 6. Reflection questions

**1. Depth versus nonlinearity.**
- Depth alone did nothing. A 2–2–1 network with no activation got exactly what
  the plain linear model got: loss 0.6931, P = 0.5 everywhere, 2/4.
- Adding the tanh nonlinearity to the same 2–2–1 shape solved XOR (loss 0.0002,
  4/4). The hidden units became two "exactly one sensor on" detectors.
- So the extra layer only helps because it is nonlinear.

**2. Evidence that backpropagation gave a useful signal, not just a non-zero one:**
- the loss fell from 0.7152 to 0.000206;
- one step against the gradient lowered the loss;
- the gradient matched finite differences, so it is the *true* slope;
- the hidden units developed distinct, interpretable features that were never
  specified.

The Part C all-zero case is the contrast: a zero gradient, and nothing learned.

**3. Why identical or zero initialisation stops the hidden units learning different features.**
Identical units compute the same output and receive the same error signal, so
they get the same update and stay identical. With weights of 0.5 the rows moved
from 0.5 to 5.72 but stayed equal at every step, and the network was capped at
3/4. All zeros is worse: tanh(0) = 0 and W⁽²⁾ = 0 make every gradient except the
output bias's zero, and XOR's two-and-two labels make that one zero too, so
nothing moves at all.

**4. How the hidden activation affected the gradient.**
- *Engineering observation:* the early gradient norms were
  sigmoid 0.0009, tanh 0.0618, ReLU 0.0017. Sigmoid and tanh solved seed 0;
  ReLU stopped at 3/4. Over 20 seeds they solved 15, 14 and 3.
- *Scientific explanation:* sigmoid's derivative is at most 0.25, and its
  near-constant outputs made the balanced XOR examples' gradients cancel 59×.
  ReLU's derivative is exactly 0 for negative inputs, and one of the two units
  died, leaving too few units for XOR.

The observation is *what* was measured. The explanation is *why*, and it was
checked by measuring the per-example gradients and pre-activations, not assumed.

**5. Why the output layer and loss must be chosen together.** The output
activation decides what the numbers mean: one probability for a yes/no answer,
or a distribution over K classes. The loss must be the negative log-likelihood
of *that* distribution. Matched pairs (sigmoid + BCE, softmax + cross-entropy)
give the clean p − y gradient. Mismatched pairs cause problems:
- sigmoid + squared error gives a gradient that shrinks when the answer is
  confidently wrong;
- softmax followed by `CrossEntropyLoss` applies softmax twice.

PyTorch fuses each pair (`BCEWithLogitsLoss`, `CrossEntropyLoss`) because the
separate versions are numerically unsafe. In the +100 diagnostic the naive
softmax produced `nan`.

**6. Where the LLM helped, and where human checking was essential.**
- *Helped:* it produced a correct PyTorch training loop in seconds, with the
  right logits + `BCEWithLogitsLoss` pairing (no double sigmoid). Its
  three-class change was correct first time.
- *Human checking was essential:* its own tests would have passed a setup that
  **fails on 11 of 20 seeds**. They also measured the wrong moments: the final
  loss came from before the last update, and the gradient check could only
  pass on a *failed* run. Only running it across seeds, and reading the code
  against the design, caught this.

**7. Which tests to keep when scaling up.**
- **Keep:**
  - loss curves and held-out accuracy;
  - per-layer gradient norms;
  - dead-unit and saturation statistics taken from the pre-activations;
  - the check that probabilities sum to 1;
  - the p − y check on the output logits;
  - a few repeated seeds;
  - an initialisation sanity check, to rule out symmetric starts.
- **Too expensive:**
  - exhaustive finite-difference gradient checks: two forward passes *per
    parameter*, which is billions;
  - large seed sweeps;
  - inspecting every weight row by hand.

  Instead, run finite differences on a random sample of parameters, or on a
  tiny copy of the model (e.g. `torch.autograd.gradcheck` on one layer).
