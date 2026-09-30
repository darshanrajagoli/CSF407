# Prompts given to the LLM, the code it generated, and what was changed

**CS F407 Artificial Intelligence** · Laboratory: Neural Models
**LLM used:** Claude (Anthropic)

The Task 1 specification and the Task 2 design (`LAB_REPORT.md` §1–§2) were
written **before** any prompt was sent, as the handout requires.

---

## Prompt 1: the binary XOR network (Task 3)

> Generate minimal PyTorch code for the following model and dataset. Do not
> change the architecture or task.
>
> - Data: the four XOR examples, written out explicitly:
>   (0,0) → 0, (0,1) → 1, (1,0) → 1, (1,1) → 0.
> - Model: a 2–2–1 network. Hidden activation tanh. One output **logit**,
>   trained with `BCEWithLogitsLoss`. Apply a sigmoid only to report probabilities.
> - Random weight initialisation (PyTorch's default).
> - Full-batch training for 3000 steps on the CPU, with Adam at learning rate 0.05.
> - After training, report the final loss, all four probabilities, the
>   thresholded labels (threshold 0.5), and the gradient tensor of the
>   first-layer weights after `backward()`.
>
> Set a random seed for reproducibility and explain each test in one sentence.

### The generated code (verbatim)

```python
import torch
import torch.nn as nn

torch.manual_seed(0)

# The four XOR examples
X = torch.tensor([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
y = torch.tensor([[0.], [1.], [1.], [0.]])

# 2-2-1 network: tanh hidden layer, one output logit
model = nn.Sequential(
    nn.Linear(2, 2),
    nn.Tanh(),
    nn.Linear(2, 1),
)

loss_fn = nn.BCEWithLogitsLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.05)

for step in range(3000):
    optimizer.zero_grad()
    logits = model(X)            # forward pass
    loss = loss_fn(logits, y)    # scalar loss
    loss.backward()              # reverse-mode autodiff
    optimizer.step()             # parameter update

print("final loss:", loss.item())

with torch.no_grad():
    probs = torch.sigmoid(model(X))
    labels = (probs > 0.5).float()
print("probabilities:", probs.squeeze().tolist())
print("labels:", labels.squeeze().tolist())
print("all correct:", torch.equal(labels, y))

print("first-layer weight gradient:\n", model[0].weight.grad)

# Tests:
# - final loss should be close to 0, showing the model fits the data.
# - all four thresholded labels should equal y, showing XOR was learned.
# - the gradient tensor should be non-zero, showing backpropagation reached the first layer.
```

### Inspected before running

The handout asks where the four steps happen:

| Step | Where |
|---|---|
| forward pass | `logits = model(X)` |
| scalar loss formed | `loss = loss_fn(logits, y)`: the mean BCE over the 4 examples |
| reverse-mode AD invoked | `loss.backward()` |
| optimiser changes parameters | `optimizer.step()` |

The architecture and the task were checked against the Task 2 design:
- 2–2–1 with tanh;
- one logit fed to `BCEWithLogitsLoss`, with no sigmoid inside the model, so the
  sigmoid is not applied twice;
- all four examples, trained full-batch.

These all matched.

**Two changes made before running:**

1. **The "final loss" was reported for the wrong weights.** `loss` is computed
   *before* the last `optimizer.step()`, so it belongs to the parameters one
   step earlier than the probabilities printed below it. The fix is to compute
   the final loss again after training (`loss_now()` in `neural_xor.py`).
2. **The gradient test checked the wrong moment.** It prints the gradient from
   the *last* step. When training works, that gradient is close to zero, so
   "the gradient should be non-zero" can't pass for a good run. The fix: take
   the gradient **at the start of training**, where a non-zero value really
   shows the signal reaches the first layer. Also check it against finite
   differences (Part B). The final gradient is reported separately, with the
   note that near zero is expected.

### Found by running it

Seed 0 learned XOR: 4/4 correct, loss 8e-5. But a single run is not evidence.
Across seeds 0–19, **only 9 of 20 runs learned XOR.** 9 of the 11 failures
stopped at loss 0.3466 = ln 2 / 2: two examples right, two stuck at probability
0.5. The other 2 stopped at 0.4774 with three inputs at probability 0.67.

Changing the learning rate and optimiser is an allowed engineering setting under
Task 4A. Each setting was tried on 50 seeds with the same tanh network:

| Optimiser | Seeds solved (of 50) |
|---|---|
| Adam, lr 0.05 (the LLM's choice) | 27 |
| Adam, lr 0.1 | 21 |
| SGD + momentum 0.9, lr 0.1 | 38 |
| **SGD + momentum 0.9, lr 0.5** | **41** |

Each row is the LLM's code above run on seeds 0–49 with only the optimiser line
changed; a seed counts as solved if all four thresholded labels are correct.

The final code uses SGD with momentum 0.9 and lr 0.5. The model, data, loss and
step count are unchanged. It still fails on some seeds (14/20 in
`results.txt`). That is a property of a network with only two hidden units, and
the report says so (Part D).

---

## Prompt 2: the three-class output (Task 5)

Written down before the prompt was sent: the last weight matrix should be
3 × 2, there should be 3 logits per example, and the targets should be class
indices 0/1/2.

> Modify only the output and loss portion of the previous code. The same four
> sensor inputs now have three classes: (0,0) → 0, (0,1) and (1,0) → 1,
> (1,1) → 2. Keep the 2 tanh hidden units. Replace the single output with three
> logits and train with multiclass cross-entropy. Report the softmax
> probabilities for all four inputs, the predicted classes, and the sum of one
> probability vector.

### What changed in the generated code

```python
y = torch.tensor([0, 1, 1, 2])          # class indices: none / disagree / both active
...
    nn.Linear(2, 3),                    # changed: three logits instead of one
...
loss_fn = nn.CrossEntropyLoss()         # changed: softmax + cross-entropy on raw logits
...
    probs = torch.softmax(model(X), dim=1)
    print("predicted:", probs.argmax(dim=1).tolist())
    print("sum of probabilities for x=(0,1):", probs[1].sum().item())
```

### Inspected before running

- **Only the output and loss changed.** The hidden layer, optimiser and data
  inputs are untouched.
- **No softmax inside the model.** `CrossEntropyLoss` applies it itself.
  Softmax followed by `CrossEntropyLoss` would apply it twice.
- **Targets have the right form.** They are class indices of type `long` with
  shape `[4]`, which is what `CrossEntropyLoss` expects. They are not one-hot
  and not shape `[4, 1]`.

Nothing needed changing. Run as given (on the LLM's Adam code, seed 0), it
predicts all four classes correctly with loss about 4×10⁻⁵, and the softmax row
sums to 1.0. `neural_xor.py`, with the SGD settings, also gets 4/4 (loss 0.000109).

---

## Who wrote what

| Part | Written by |
|---|---|
| Task 1 specification, Task 2 design and validation criteria | written before prompting (`LAB_REPORT.md` §1–§2) |
| The first binary network and the three-class change | the LLM, from the prompts above |
| `neural_xor.py`: the final code, with the fixes above and the Part B–D and Task 5 experiments | the LLM, building on the checked draft. Every result was checked by running it |
| What counts as success, the inspection and the diagnoses (e.g. why sigmoid's gradient is small) | checked by hand against the code's output |
