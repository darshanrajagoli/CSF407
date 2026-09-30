"""Second-order autoregressive language model:  P(X_t | X_{t-2}, X_{t-1}).

The Bayesian network now gives every word two parents:  X_{t-2} -> X_t <- X_{t-1}.
For four tokens:  P(X1,X2,X3,X4) = P(X1) P(X2|X1) P(X3|X1,X2) P(X4|X2,X3).

Each sentence is padded with TWO <START> tokens so that the first two words
also have a two-word context:
    P(X1)    is stored as  P(X1 | <START>, <START>)
    P(X2|X1) is stored as  P(X2 | <START>, X1)
The CPT is estimated by counting observed triples:

    P(w_k | w_i, w_j) = C(w_i, w_j, w_k) / sum_m C(w_i, w_j, w_m)
"""
import random
from collections import defaultdict

from bigram_model import END, MAX_TOKENS, START, load_corpus, most_probable, sample_from


def tokenise2(sentence):
    """'the cat' -> ['<START>', '<START>', 'the', 'cat', '<END>']"""
    return [START, START] + sentence.lower().split() + [END]


class TrigramModel:
    def __init__(self):
        # counts[(w_i, w_j)][w_k] = how many times w_k followed the pair (w_i, w_j)
        self.counts = defaultdict(lambda: defaultdict(int))
        self.probs = {}

    def train(self, sentences):
        for sentence in sentences:
            tokens = tokenise2(sentence)
            for a, b, c in zip(tokens, tokens[1:], tokens[2:]):
                self.counts[(a, b)][c] += 1
        for context, nexts in self.counts.items():
            total = sum(nexts.values())
            self.probs[context] = {w: n / total for w, n in nexts.items()}
        return self

    def distribution(self, w2, w1):
        """P(. | X_{t-2}=w2, X_{t-1}=w1). An unseen pair returns {}."""
        return self.probs.get((w2, w1), {})

    def show(self, w2, w1):
        dist = self.distribution(w2, w1)
        if not dist:
            print(f"  ({w2}, {w1}): no transitions observed")
            return
        total = sum(self.counts[(w2, w1)].values())
        for w, p in sorted(dist.items(), key=lambda x: -x[1]):
            print(f"  P({w:<7}| {w2}, {w1}) = {self.counts[(w2, w1)][w]}/{total} = {p:.3f}")

    def predict(self, w2, w1):
        dist = self.distribution(w2, w1)
        return most_probable(dist) if dist else None

    def generate(self, mode="sample", rng=random):
        tokens = [START, START]
        while tokens[-1] != END and len(tokens) <= MAX_TOKENS + 1:
            dist = self.distribution(tokens[-2], tokens[-1])
            if not dist:
                break
            tokens.append(most_probable(dist) if mode == "greedy" else sample_from(dist, rng))
        return " ".join(t for t in tokens if t not in (START, END))


if __name__ == "__main__":
    model = TrigramModel().train(load_corpus())
    for context in [(START, START), (START, "the"), ("the", "cat"), ("the", "dog"), ("sat", "on"), ("on", "the")]:
        print(f"P(next | {context[0]}, {context[1]}):")
        model.show(*context)
    rng = random.Random(0)
    print("\nsampled:", [model.generate("sample", rng) for _ in range(3)])
    print("greedy: ", model.generate("greedy"))
