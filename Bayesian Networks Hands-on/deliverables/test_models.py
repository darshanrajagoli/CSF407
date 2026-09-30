"""Tests for both models: properties that must hold if the probability model is right.

    python test_models.py        (no pytest needed)
"""
import random

from bigram_model import END, MAX_TOKENS, START, BigramModel, load_corpus, sample_from, tokenise
from trigram_model import TrigramModel, tokenise2

passed = failed = 0


def check(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}")


def rows_sum_to_one(probs):
    return all(abs(sum(d.values()) - 1.0) < 1e-9 for d in probs.values())


def close(a, b, tol=1e-9):
    return abs(a - b) < tol


def sentence_probability(model, sentence):
    """Chain rule with the first-order assumption: product of P(x_t | x_{t-1})."""
    tokens = tokenise(sentence)
    p = 1.0
    for prev, nxt in zip(tokens, tokens[1:]):
        p *= model.distribution(prev).get(nxt, 0.0)
    return p


corpus = load_corpus()
bi = BigramModel().train(corpus)
tri = TrigramModel().train(corpus)

print("First-order model  P(X_t | X_{t-1})")
check("tokenise adds <START> and <END> and lower-cases",
      tokenise("The Cat") == [START, "the", "cat", END])
check("counts: C(the, cat) = 3, C(sat, on) = 4", bi.counts["the"]["cat"] == 3 and bi.counts["sat"]["on"] == 4)
check("42 transitions counted in total (6 sentences x 7)",
      sum(sum(r.values()) for r in bi.counts.values()) == 42)
check("P(cat | the) = 3/12 and P(park | the) = 2/12",
      close(bi.distribution("the")["cat"], 3 / 12) and close(bi.distribution("the")["park"], 2 / 12))
check("handout's own example: 'the cat' x3, 'the dog' x2 gives 3/5 and 2/5",
      (lambda m: close(m.distribution("the")["cat"], 0.6) and close(m.distribution("the")["dog"], 0.4))(
          BigramModel().train(["the cat"] * 3 + ["the dog"] * 2)))
check("NORMALISATION: every row sums to 1", rows_sum_to_one(bi.probs))
check("every probability is between 0 and 1",
      all(0 < p <= 1 for d in bi.probs.values() for p in d.values()))
check("zero-probability transition: P(sat | the) = 0", bi.distribution("the").get("sat", 0) == 0)
check("<END> is never a context (nothing comes after the end)", END not in bi.probs)
check("unseen word: empty distribution and predict() = None, no crash",
      bi.distribution("bird") == {} and bi.predict("bird") is None)
check("greedy picks the argmax: predict(cat) = sat, predict(ran) = to",
      bi.predict("cat") == "sat" and bi.predict("ran") == "to")
check("greedy is deterministic", len({bi.generate("greedy") for _ in range(5)}) == 1)
check(f"greedy stops at the {MAX_TOKENS}-word cap instead of looping forever",
      len(bi.generate("greedy").split()) == MAX_TOKENS)

rng = random.Random(0)
draws = [bi.generate("sample", rng) for _ in range(300)]
check("every sampled sentence has probability > 0 under the model",
      all(sentence_probability(bi, s) > 0 for s in draws if len(s.split()) < MAX_TOKENS))

rng = random.Random(1)
n = 60000
nexts = [sample_from(bi.distribution("the"), rng) for _ in range(n)]
freq = {w: nexts.count(w) / n for w in bi.distribution("the")}
check("SAMPLING follows the CPT: frequencies after 'the' within 0.01 of P(. | the)",
      all(abs(freq[w] - p) < 0.01 for w, p in bi.distribution("the").items()))

rng = random.Random(2)
sents = [bi.generate("sample", rng) for _ in range(20000)]
p_model = sentence_probability(bi, "the park")
check(f"chain rule: share of 'the park' in samples matches P = 1 x 2/12 x 1 = {p_model:.3f}",
      abs(sents.count("the park") / len(sents) - p_model) < 0.01)

broken = {w: dict(d) for w, d in bi.probs.items()}
del broken["the"]["park"]  # simulate a bug that loses one entry -> row sums to 0.833
check("the normalisation test CATCHES a broken table (a row summing to 0.833)", not rows_sum_to_one(broken))

print("\nSecond-order model  P(X_t | X_{t-2}, X_{t-1})")
check("tokenise2 pads with two <START> tokens", tokenise2("the cat") == [START, START, "the", "cat", END])
check("NORMALISATION: every row sums to 1", rows_sum_to_one(tri.probs))
check("P(X1) is stored as P(the | <START>, <START>) = 1", close(tri.distribution(START, START)["the"], 1.0))
check("P(cat | <START>, the) = 3/6", close(tri.distribution(START, "the")["cat"], 0.5))
check("P(mat | on, the) = 2/4 and P(park | to, the) = 2/2",
      close(tri.distribution("on", "the")["mat"], 0.5) and close(tri.distribution("to", "the")["park"], 1.0))
check("more context changes the prediction: P(mat | on, the) = 0.5 but P(mat | the) = 0.167",
      close(tri.distribution("on", "the")["mat"], 0.5) and close(bi.distribution("the")["mat"], 2 / 12))
check("unseen pair (the, the): empty distribution and predict() = None",
      tri.distribution("the", "the") == {} and tri.predict("the", "the") is None)
check("greedy reaches <END>: 'the cat sat on the mat'", tri.generate("greedy") == "the cat sat on the mat")
rng = random.Random(3)
check("with this tiny corpus every sampled sentence is a training sentence",
      all(tri.generate("sample", rng) in set(corpus) for _ in range(500)))

print(f"\n{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
