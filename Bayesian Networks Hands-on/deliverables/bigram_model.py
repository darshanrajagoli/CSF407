"""First-order autoregressive language model:  P(X_t | X_{t-1}).

The Bayesian network is a chain  X1 -> X2 -> X3 -> ... -> X_T.
Each word depends only on the word just before it, so the model is one
conditional probability table (CPT): for every previous word, a distribution
over the next word. The table is estimated by counting:

    P(w_j | w_i) = C(w_i, w_j) / sum_k C(w_i, w_k)

Plain Python only - no machine-learning library, no pretrained model.
"""
import random
from collections import defaultdict
from pathlib import Path

START, END = "<START>", "<END>"
MAX_TOKENS = 20  # safety cap: greedy mode can loop forever without it (see LAB_REPORT.md)
CORPUS = Path(__file__).with_name("corpus.txt")


def load_corpus(path=CORPUS):
    """Read one sentence per line, lower-cased, blank lines skipped."""
    with open(path, encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]


def tokenise(sentence):
    """'The cat sat' -> ['<START>', 'the', 'cat', 'sat', '<END>']"""
    return [START] + sentence.lower().split() + [END]


def sample_from(dist, rng):
    """Draw one word from a {word: probability} distribution."""
    words = list(dist)
    return rng.choices(words, weights=[dist[w] for w in words])[0]


def most_probable(dist):
    """argmax_w P(w). Ties go to the word seen first in training (dicts keep insertion order)."""
    return max(dist, key=dist.get)


class BigramModel:
    def __init__(self):
        # counts[prev][next] = how many times `next` followed `prev` in training
        self.counts = defaultdict(lambda: defaultdict(int))
        # probs[prev][next] = P(next | prev)  -- the CPT
        self.probs = {}

    def train(self, sentences):
        for sentence in sentences:
            tokens = tokenise(sentence)
            for prev, nxt in zip(tokens, tokens[1:]):
                self.counts[prev][nxt] += 1
        for prev, nexts in self.counts.items():
            total = sum(nexts.values())
            self.probs[prev] = {w: c / total for w, c in nexts.items()}
        return self

    def distribution(self, prev):
        """P(. | prev). An unseen word has no row in the CPT, so this returns {}."""
        return self.probs.get(prev, {})

    def show(self, prev):
        dist = self.distribution(prev)
        if not dist:
            print(f"  '{prev}': no transitions observed - the model has nothing to say")
            return
        for w, p in sorted(dist.items(), key=lambda x: -x[1]):
            print(f"  P({w:<7}| {prev}) = {self.counts[prev][w]}/{sum(self.counts[prev].values())} = {p:.3f}")

    def predict(self, prev):
        """Most probable next word, or None for an unseen word."""
        dist = self.distribution(prev)
        return most_probable(dist) if dist else None

    def generate(self, mode="sample", rng=random):
        """mode='sample': X_t ~ P(X_t | X_{t-1}).  mode='greedy': X_t = argmax P(X_t | X_{t-1})."""
        tokens = [START]
        while tokens[-1] != END and len(tokens) <= MAX_TOKENS:
            dist = self.distribution(tokens[-1])
            if not dist:
                break
            tokens.append(most_probable(dist) if mode == "greedy" else sample_from(dist, rng))
        return " ".join(t for t in tokens if t not in (START, END))


if __name__ == "__main__":
    model = BigramModel().train(load_corpus())
    for word in ["the", "cat", "dog", "sat", "ran"]:
        print(f"P(next | {word}):")
        model.show(word)
    rng = random.Random(0)
    print("\nsampled:", [model.generate("sample", rng) for _ in range(3)])
    print("greedy: ", model.generate("greedy"))
