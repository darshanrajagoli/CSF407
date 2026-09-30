"""CS F407 Lab - Neural Models: learning, depth, activations and output layers.

One file for the whole lab. Run it with

    python neural_xor.py

It prints every result and saves the same text to results.txt.
CPU only, about two minutes, and fully seeded, so it prints the same numbers every run.

Sections: Task 1 check (linear model) - Task 4 Part A (learning) - Part B (gradients)
- Part C (symmetry) - Part D (activations) - Task 5 (three classes + softmax diagnostic).
"""
import copy
from pathlib import Path

import torch
import torch.nn as nn

torch.set_num_threads(1)  # tiny network: one thread is faster and keeps runs repeatable

# ------------------------------------------------------------------ data and settings
X = torch.tensor([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
Y_XOR = torch.tensor([[0.], [1.], [1.], [0.]])  # disagreement warning
Y_3 = torch.tensor([0, 1, 1, 2])                # Task 5: none / disagree / both active

ACTIVATIONS = {"sigmoid": nn.Sigmoid, "tanh": nn.Tanh, "relu": nn.ReLU}
NO_ACTIVATION = nn.Identity  # a hidden layer with no nonlinearity (used in the Task 1 check only)
SEED = 0
STEPS = 3000
LR, MOMENTUM = 0.5, 0.9  # plain SGD with momentum (see LAB_REPORT.md, Task 4A, for why)
N_SEEDS = 20             # for the repeated-run check

lines = []


def out(text=""):
    print(text)
    lines.append(text)


def heading(text):
    out()
    out("=" * 70)
    out(text)
    out("=" * 70)


def make_net(activation="tanh", n_out=1, seed=SEED):
    """2 inputs -> 2 hidden units -> n_out logits. Same seed = same starting weights."""
    torch.manual_seed(seed)
    act = NO_ACTIVATION if activation == "none" else ACTIVATIONS[activation]
    return nn.Sequential(nn.Linear(2, 2), act(), nn.Linear(2, n_out))


def train(net, y, loss_fn, steps=STEPS, watch=None):
    """Full-batch gradient descent. `watch(step, net)` is called after backward(), before the update."""
    opt = torch.optim.SGD(net.parameters(), lr=LR, momentum=MOMENTUM)
    for step in range(steps):
        opt.zero_grad()
        loss = loss_fn(net(X), y)  # forward pass, then one scalar loss
        loss.backward()            # backpropagation: every p.grad becomes dL/dp
        if watch:
            watch(step, net)
        opt.step()                 # the optimiser changes the parameters
    return net


def loss_now(net, y, loss_fn):
    with torch.no_grad():
        return loss_fn(net(X), y).item()


def first_layer_grad(net, y, loss_fn):
    """dL/dW1 at the current parameters."""
    net.zero_grad()
    loss_fn(net(X), y).backward()
    return net[0].weight.grad.clone()


def predict(net):
    with torch.no_grad():
        p = torch.sigmoid(net(X)).squeeze(1)
    return p, (p > 0.5).float()


def fmt(t):
    return "[" + ", ".join(f"{v:.4f}" for v in t.flatten().tolist()) + "]"


bce = nn.BCEWithLogitsLoss()  # sigmoid + binary cross-entropy in one numerically stable step

# ------------------------------------------------------------------ Task 1
heading("TASK 1 CHECK - one affine map + sigmoid (no hidden layer)")
torch.manual_seed(SEED)
linear = nn.Linear(2, 1)
opt = torch.optim.SGD(linear.parameters(), lr=LR, momentum=MOMENTUM)
for _ in range(STEPS):
    opt.zero_grad()
    bce(linear(X), Y_XOR).backward()
    opt.step()
p_lin, _ = predict(linear)
out(f"  final loss {loss_now(linear, Y_XOR, bce):.4f}   (ln 2 = 0.6931: the loss of answering 0.5 every time)")
out(f"  probabilities {fmt(p_lin)}, correct {int((predict(linear)[1] == Y_XOR.squeeze(1)).sum())}/4"
    "   -> every point is left at 0.5: no straight line separates XOR")

deep_linear = train(make_net("none"), Y_XOR, bce)
p_dl, l_dl = predict(deep_linear)
out(f"  same check with a hidden layer but NO activation (2 -> 2 -> 1, all affine):")
out(f"  final loss {loss_now(deep_linear, Y_XOR, bce):.4f}, probabilities {fmt(p_dl)},"
    f" correct {int((l_dl == Y_XOR.squeeze(1)).sum())}/4   -> extra depth alone does not help")

# ------------------------------------------------------------------ Task 4 Part A
heading("TASK 4 PART A - basic learning check (tanh, seed 0)")
net = make_net("tanh")
loss0 = loss_now(net, Y_XOR, bce)
grad0 = first_layer_grad(net, Y_XOR, bce)  # kept for Part B
train(net, Y_XOR, bce)
lossT = loss_now(net, Y_XOR, bce)
p, labels = predict(net)
out(f"  initial loss {loss0:.4f}")
out(f"  final loss   {lossT:.6f}   (recomputed after the last update)")
for x, pi, li, yi in zip(X.tolist(), p.tolist(), labels.tolist(), Y_XOR.squeeze(1).tolist()):
    out(f"  x = {x}  P(warning) = {pi:.4f}  label = {int(li)}  target = {int(yi)}")
correct = int((labels == Y_XOR.squeeze(1)).sum())
out(f"  correct: {correct}/4")
with torch.no_grad():
    h = net[1](net[0](X))
out("  what the two hidden units learned (tanh outputs for the four inputs):")
out(f"    unit 1: {fmt(h[:, 0])}")
out(f"    unit 2: {fmt(h[:, 1])}")

# ------------------------------------------------------------------ Task 4 Part B
heading("TASK 4 PART B - backpropagation check")
out("  dL/dW1 at the start of training (row i = hidden unit i, column j = input x_j):")
out(f"    unit 1 row: {fmt(grad0[0])}")
out(f"    unit 2 row: {fmt(grad0[1])}")
out(f"  dL/dW1 after training: max |entry| = {first_layer_grad(net, Y_XOR, bce).abs().max():.2e}"
    "   (near 0 because the loss is near its minimum)")

fresh = make_net("tanh")
g_mean = first_layer_grad(fresh, Y_XOR, bce)
per_example = []
for i in range(4):
    fresh.zero_grad()
    bce(fresh(X[i:i + 1]), Y_XOR[i:i + 1]).backward()
    per_example.append(fresh[0].weight.grad.clone())
g_avg = torch.stack(per_example).mean(0)
out(f"  mean loss -> gradient = average of the 4 per-example gradients: "
    f"max difference {(g_mean - g_avg).abs().max():.1e}")

# Finite differences on a float64 copy (float32 roundoff would swamp the small entries).
eps = 1e-6
net64, X64, Y64 = copy.deepcopy(fresh).double(), X.double(), Y_XOR.double()
g_fd = torch.zeros(2, 2, dtype=torch.float64)
with torch.no_grad():
    W = net64[0].weight
    for i in range(2):
        for j in range(2):
            W[i, j] += eps
            up = bce(net64(X64), Y64).item()
            W[i, j] -= 2 * eps
            down = bce(net64(X64), Y64).item()
            W[i, j] += eps
            g_fd[i, j] = (up - down) / (2 * eps)
out(f"  finite-difference check (float64, nudge each weight by +-{eps:g}): {fmt(g_fd)}")
out(f"    max difference from backward() {(g_mean.double() - g_fd).abs().max():.1e},"
    f" largest relative difference {((g_mean.double() - g_fd) / g_fd).abs().max():.1e}")

first_layer_grad(fresh, Y_XOR, bce)  # refresh .grad on every parameter with the full-batch gradient
with torch.no_grad():
    before = bce(fresh(X), Y_XOR).item()
    for prm in fresh.parameters():
        prm -= 0.01 * prm.grad
    after = bce(fresh(X), Y_XOR).item()
out(f"  one small step against the gradient: loss {before:.5f} -> {after:.5f}"
    f"  ({'down' if after < before else 'NOT down'}: the gradient points somewhere useful)")

# ------------------------------------------------------------------ Task 4 Part C
heading("TASK 4 PART C - symmetry: identical starting weights (tanh, architecture unchanged)")
for label, value in [("every weight and bias = 0 (the handout's case)", 0.0),
                     ("every weight and bias = 0.5 (same idea, non-zero)", 0.5)]:
    net_z = make_net("tanh")
    with torch.no_grad():
        for prm in net_z.parameters():
            prm.fill_(value)
    snapshots, grad0_max = {}, []

    def watch(step, n, snaps=snapshots):
        if step == 0:
            grad0_max.append(max(prm.grad.abs().max().item() for prm in n.parameters()))
        if step in (0, 1, 10, 100, STEPS - 1):
            snaps[step] = n[0].weight.detach().clone()

    train(net_z, Y_XOR, bce, watch=watch)
    out(f"  {label}:  largest |gradient| of any parameter at step 0 = {grad0_max[0]:.1e}")
    out("    rows of W1 (unit 1 | unit 2), recorded before each step's update:")
    for step, Wz in snapshots.items():
        out(f"    step {step:>4}: {fmt(Wz[0])} | {fmt(Wz[1])}   identical: {torch.equal(Wz[0], Wz[1])}")
    pz, lz = predict(net_z)
    out(f"    after training: P = {fmt(pz)}, correct {int((lz == Y_XOR.squeeze(1)).sum())}/4,"
        f" loss {loss_now(net_z, Y_XOR, bce):.4f}")

# ------------------------------------------------------------------ Task 4 Part D
heading("TASK 4 PART D - hidden activation experiment (same starting weights, seed 0)")
out(f"  {'activation':<10}{'final loss':>12}{'4/4 correct?':>14}{'early ||dL/dW1||':>18}"
    f"{'solved, ' + str(N_SEEDS) + ' seeds':>18}")
diagnostics = []
for act in ACTIVATIONS:
    net_a = make_net(act)
    g_early = first_layer_grad(net_a, Y_XOR, bce).norm().item()  # step 0, before any update
    with torch.no_grad():
        pre0 = net_a[0](X)  # hidden pre-activations at the start
        p0 = torch.sigmoid(net_a(X)).squeeze(1)  # starting P(warning) for the 4 inputs
    per_ex = []
    for i in range(4):  # each example's own gradient, before averaging
        net_a.zero_grad()
        bce(net_a(X[i:i + 1]), Y_XOR[i:i + 1]).backward()
        per_ex.append(net_a[0].weight.grad.norm().item())
    per_ex_mean = sum(per_ex) / 4
    train(net_a, Y_XOR, bce)
    _, la = predict(net_a)
    ok = int((la == Y_XOR.squeeze(1)).sum())
    solved = 0
    for s in range(N_SEEDS):
        n_s = train(make_net(act, seed=s), Y_XOR, bce)
        solved += int(torch.equal(predict(n_s)[1], Y_XOR.squeeze(1)))
    out(f"  {act:<10}{loss_now(net_a, Y_XOR, bce):>12.6f}{('yes' if ok == 4 else f'no ({ok}/4)'):>14}"
        f"{g_early:>18.4f}{f'{solved}/{N_SEEDS}':>18}")
    with torch.no_grad():
        preT = net_a[0](X)
    diagnostics.append((act, pre0, preT, p0, per_ex_mean, g_early))

out("\n  why the early gradients differ (step 0, same starting weights; a = W1 x + b1):")
for act, pre0, preT, p0, per_ex_mean, g_early in diagnostics:
    out(f"  {act + ':':<9}starting P(warning) = {fmt(p0)}")
    out(f"           average single-example ||dL/dW1|| = {per_ex_mean:.4f}, but the mean over all 4 = {g_early:.4f}"
        f"  (the four examples cancel {per_ex_mean / g_early:.0f}x)")
    if act == "sigmoid":
        s = torch.sigmoid(pre0)
        out(f"           derivative s(1-s) per (input, unit) = {fmt(s * (1 - s))}  (never above 0.25)")
    if act == "tanh":
        out(f"           derivative 1 - tanh^2 per (input, unit) = {fmt(1 - torch.tanh(pre0) ** 2)}  (up to 1)")
    if act == "relu":
        out(f"           pre-activation a > 0 (derivative 1) for {int((pre0 > 0).sum())}/8 (input, unit) pairs, else derivative 0")
        dead = [(preT[:, u] <= 0).all().item() for u in range(2)]
        out(f"           after training, units with a <= 0 on all 4 inputs (dead): {sum(dead)}/2")

# ------------------------------------------------------------------ Task 5
heading("TASK 5 - three classes: 2 -> 2 -> 3 logits, softmax + cross-entropy")
ce = nn.CrossEntropyLoss()  # softmax + cross-entropy in one stable step; takes raw logits
net3 = make_net("tanh", n_out=3)
with torch.no_grad():
    logits_start = net3(X)  # kept for the p - y check below
out(f"  final weight matrix shape: {tuple(net3[2].weight.shape)}  (3 classes x 2 hidden units)")
out(f"  logits per example: {logits_start.shape[1]}")
out(f"  initial loss {loss_now(net3, Y_3, ce):.4f}   (ln 3 = 1.0986)")
train(net3, Y_3, ce)
with torch.no_grad():
    logits3 = net3(X)
    P3 = torch.softmax(logits3, dim=1)
out(f"  final loss {loss_now(net3, Y_3, ce):.6f}")
for x, pr, t in zip(X.tolist(), P3, Y_3.tolist()):
    out(f"  x = {x}  P(class 0,1,2) = {fmt(pr)}  predicted {int(pr.argmax())}  target {t}")
out(f"  correct: {int((P3.argmax(1) == Y_3).sum())}/4")
out(f"  example x = [0, 1]: softmax vector {fmt(P3[1])}, sum = {P3[1].sum().item():.7f}")

# p - y check at the untrained logits, where the gradient is large (after training it is ~0).
# reduction="sum" so there is no 1/4 factor from averaging.
z = logits_start.clone().requires_grad_(True)
nn.CrossEntropyLoss(reduction="sum")(z, Y_3).backward()
p_minus_y = torch.softmax(z, 1).detach() - nn.functional.one_hot(Y_3, 3).float()
out(f"  p - y check at the start of training: dL/dlogits from backward() vs p - y,"
    f" max difference {(z.grad - p_minus_y).abs().max():.1e}")
out(f"    x = [0, 1]: dL/dlogits = {fmt(z.grad[1])},  p - y = {fmt(p_minus_y[1])}")

heading("TASK 5 DIAGNOSTIC - add 100 to every logit")
z0 = logits3[1]
shifted = z0 + 100
out(f"  softmax(z)       = {fmt(torch.softmax(z0, 0))}")
out(f"  softmax(z + 100) = {fmt(torch.softmax(shifted, 0))}   "
    f"max difference {(torch.softmax(z0, 0) - torch.softmax(shifted, 0)).abs().max():.1e}")
naive = torch.exp(shifted) / torch.exp(shifted).sum()
stable = torch.exp(shifted - shifted.max()) / torch.exp(shifted - shifted.max()).sum()
out(f"  naive exp(z+100)/sum in float32: exp(z+100) = {fmt(torch.exp(shifted))} -> softmax {fmt(naive)}")
out(f"  subtract the max logit first:    softmax {fmt(stable)}")

Path(__file__).with_name("results.txt").write_text("\n".join(lines).lstrip() + "\n", encoding="utf-8")
