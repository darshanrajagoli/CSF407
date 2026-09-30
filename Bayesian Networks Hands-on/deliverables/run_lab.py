"""Runs every part of the lab and writes results.txt and generated_sentences.txt.

    python run_lab.py

Random draws use fixed seeds, so the output is the same on every run.
"""
import random
from pathlib import Path

from bigram_model import END, MAX_TOKENS, START, BigramModel, load_corpus, tokenise
from trigram_model import TrigramModel

HERE = Path(__file__).parent
lines = []


def out(text=""):
    print(text)
    lines.append(text)


def heading(text):
    out()
    out("=" * 72)
    out(text)
    out("=" * 72)


def normalisation_check(probs):
    """Part VII: for every context w, sum_v P(v | w) must be 1."""
    ok = True
    for context, dist in probs.items():
        total = sum(dist.values())
        good = abs(total - 1.0) < 1e-9
        ok = ok and good
        out(f"  {str(context):<28} sum = {total:.6f}  {'OK' if good else 'FAIL'}")
    return ok


corpus = load_corpus()
bigram = BigramModel().train(corpus)
trigram = TrigramModel().train(corpus)
vocab = sorted({w for s in corpus for w in s.split()})
outcomes = vocab + [END]  # everything that can come next

# ---------------------------------------------------------------- Part III
heading("PART III - dataset (lower-cased, one word = one token)")
for s in corpus:
    out("  " + " ".join(tokenise(s)))
out(f"\n  vocabulary ({len(vocab)} words): {', '.join(vocab)}")

# ---------------------------------------------------------------- Part IV / Q3
heading("PART IV / Q3 - first-order CPT  P(next | current)")
contexts = [START] + vocab
out("  rows = current word, columns = next word, cells = count/row total")
out("  " + " " * 8 + "".join(f"{w:>7}" for w in outcomes))
for c in contexts:
    row = bigram.counts.get(c, {})
    total = sum(row.values())
    cells = "".join(f"{(str(row[w]) + '/' + str(total)) if row.get(w) else '0':>7}" for w in outcomes)
    out(f"  {c:<8}{cells}")

out("\n  Q3 contexts in detail (and their zero-probability transitions):")
for w in ["the", "cat", "dog", "sat", "ran"]:
    out(f"\n  P(next | {w}):")
    for line_w, p in sorted(bigram.distribution(w).items(), key=lambda x: -x[1]):
        out(f"    P({line_w:<5}| {w}) = {bigram.counts[w][line_w]}/{sum(bigram.counts[w].values())} = {p:.3f}")
    zeros = [v for v in outcomes if v not in bigram.distribution(w)]
    out(f"    zero probability ({len(zeros)}): {', '.join(zeros)}")

n_nonzero = sum(len(d) for d in bigram.probs.values())
out(f"\n  whole table: {len(contexts)} x {len(outcomes)} = {len(contexts) * len(outcomes)} cells,"
    f" {n_nonzero} non-zero, {len(contexts) * len(outcomes) - n_nonzero} zero")

# ---------------------------------------------------------------- Part VII / Q8
heading("PART VII - normalisation test, first-order model")
ok1 = normalisation_check(bigram.probs)
out(f"  -> {'all rows sum to 1' if ok1 else 'SOME ROWS DO NOT SUM TO 1'}")

# ---------------------------------------------------------------- Part VIII / Q9
heading("PART VIII / Q9 - next-word prediction, argmax_w P(w | context)")
for w in [START, "the", "cat", "dog", "sat", "ran", "on", "to", "mat"]:
    dist = bigram.distribution(w)
    best_p = max(dist.values())
    tied = [v for v, p in dist.items() if p == best_p]
    shown = ", ".join(f"{v}:{p:.3f}" for v, p in sorted(dist.items(), key=lambda x: -x[1]))
    note = f"   (tie between {' and '.join(tied)})" if len(tied) > 1 else ""
    out(f"  {w:<8} -> {bigram.predict(w):<6} [{shown}]{note}")
out(f"  {'bird':<8} -> {bigram.predict('bird')}   (unseen word: no row in the CPT)")

# ---------------------------------------------------------------- Part IX
heading("PART IX - 20 sentences sampled from the first-order model (seed 1)")
rng = random.Random(1)
sampled20 = [bigram.generate("sample", rng) for _ in range(20)]
training = set(corpus)
for i, s in enumerate(sampled20, 1):
    out(f"  {i:>2}. {s}{'' if s in training else '   <- not in training data'}")
out(f"\n  distinct: {len(set(sampled20))}/20, not in training data: {sum(s not in training for s in sampled20)}/20")

# ---------------------------------------------------------------- Part X / Q10
heading("PART X / Q10 - greedy vs sampling, five sentences each")
rng = random.Random(2)
out("  Mode A, greedy (argmax every step):")
greedy5 = [bigram.generate("greedy") for _ in range(5)]
for s in greedy5:
    capped = len(s.split()) >= MAX_TOKENS
    out(f"    {s}" + (f"   [cut off at the {MAX_TOKENS}-word cap - never reached <END>]" if capped else ""))
out("  Mode B, sampling:")
sample5 = [bigram.generate("sample", rng) for _ in range(5)]
for s in sample5:
    out(f"    {s}")
out(f"\n  distinct sentences: greedy {len(set(greedy5))}/5, sampling {len(set(sample5))}/5")

# ---------------------------------------------------------------- Part XI-XII
heading("PART XI-XII - second-order CPT  P(next | two previous words)")
for context in sorted(trigram.probs, key=lambda c: (c[0] != START, c[1] != START, c)):
    dist = trigram.probs[context]
    total = sum(trigram.counts[context].values())
    shown = ", ".join(f"{w} {trigram.counts[context][w]}/{total}" for w in sorted(dist, key=lambda w: -dist[w]))
    out(f"  ({context[0]}, {context[1]})".ljust(26) + f"-> {shown}")

heading("PART VII (again) - normalisation test, second-order model")
ok2 = normalisation_check(trigram.probs)
out(f"  -> {'all rows sum to 1' if ok2 else 'SOME ROWS DO NOT SUM TO 1'}")

rng = random.Random(3)
out("\n  second-order, greedy: " + trigram.generate("greedy"))
out("  second-order, 5 samples:")
for _ in range(5):
    out("    " + trigram.generate("sample", rng))

# ---------------------------------------------------------------- Part XIII / Q12
heading("PART XIII / Q12 - comparing the two models")
V = len(vocab)
ctx1 = 1 + V                    # <START> or any word
ctx2 = 1 + V + V * V            # (<START>,<START>), (<START>, w), (w, w')
nz2 = sum(len(d) for d in trigram.probs.values())
out(f"  {'':<40}{'first-order':>14}{'second-order':>14}")
out(f"  {'possible contexts':<40}{ctx1:>14}{ctx2:>14}")
out(f"  {'CPT cells (contexts x 11 outcomes)':<40}{ctx1 * len(outcomes):>14}{ctx2 * len(outcomes):>14}")
out(f"  {'free parameters (contexts x 10)':<40}{ctx1 * (len(outcomes) - 1):>14}{ctx2 * (len(outcomes) - 1):>14}")
out(f"  {'non-zero probabilities actually learned':<40}{n_nonzero:>14}{nz2:>14}")
out(f"  {'contexts seen in training':<40}{len(bigram.probs):>14}{len(trigram.probs):>14}")
out(f"  {'zero-probability (never seen) contexts':<40}{ctx1 - len(bigram.probs):>14}{ctx2 - len(trigram.probs):>14}")
out(f"  {'training events (transitions counted)':<40}{sum(len(tokenise(s)) - 1 for s in corpus):>14}"
    f"{sum(len(tokenise(s)) - 1 for s in corpus):>14}")

N = 1000
rng = random.Random(4)
s1 = [bigram.generate("sample", rng) for _ in range(N)]
s2 = [trigram.generate("sample", rng) for _ in range(N)]
out(f"\n  diversity over {N} samples:")
for name, ss in [("first-order", s1), ("second-order", s2)]:
    novel = [s for s in ss if s not in training]
    out(f"    {name:<13} distinct sentences: {len(set(ss)):>4}   novel (not in training): "
        f"{len(novel):>4}/{N}   distinct novel: {len(set(novel))}")

out("\n  coherence - first-order sentences that are NOT in the training data (most common first):")
counts = {}
for s in s1:
    if s not in training:
        counts[s] = counts.get(s, 0) + 1
for s, c in sorted(counts.items(), key=lambda x: -x[1])[:8]:
    out(f"    {c:>4} x  {s}")
out("  coherence - second-order: every sampled sentence is one of the six training sentences:"
    f" {all(s in training for s in s2)}")

# ---------------------------------------------------------------- save
(HERE / "generated_sentences.txt").write_text(
    "First-order model, 20 sampled sentences (seed 1)\n\n" + "\n".join(sampled20)
    + "\n\nGreedy (Mode A), 5 sentences\n\n" + "\n".join(greedy5)
    + "\n\nSampling (Mode B), 5 sentences (seed 2)\n\n" + "\n".join(sample5) + "\n",
    encoding="utf-8",
)
(HERE / "results.txt").write_text("\n".join(lines).lstrip() + "\n", encoding="utf-8")
