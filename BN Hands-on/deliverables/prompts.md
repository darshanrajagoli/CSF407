# Prompts given to the LLM, and what was done with the output

**CS F407 Artificial Intelligence** · Laboratory: Bayesian Networks and Autoregressive Language Models
**LLM used:** Claude (Anthropic)

The handout says not to ask "Write a language model in Python". It says to give a
**behavioural specification** instead. Each prompt below is that kind of
specification. After each one there is a note on what came back, what was checked,
and what was changed.

---

## Prompt 1: first-order model (Part V)

> Write a simple Python implementation of a first-order autoregressive language
> model. The model should:
>
> 1. take a list of tokenised sentences as training data;
> 2. count transitions between consecutive tokens;
> 3. construct the conditional distribution P(X_t | X_{t-1});
> 4. display the probabilities for a specified previous token;
> 5. predict the most probable next token;
> 6. generate a sentence by repeatedly sampling the next token;
> 7. stop when the `<END>` token is generated.
>
> Do not use a machine-learning library or a pretrained language model. Use
> ordinary Python data structures and random sampling.
>
> Training data (lower-case, one word = one token, each sentence wrapped in
> `<START>` … `<END>`):
> the cat sat on the mat / the cat sat on the rug / the dog sat on the mat /
> the dog ran to the park / the cat ran to the park / the dog sat on the rug

**What came back:** a `BigramLanguageModel` class. It had nested-dictionary counts,
a probability table built by dividing each count by its row total, `show`,
`predict` (argmax) and `generate` (sampling with `random.choices`).

**Checks:**
- The counts were right: C(the, cat) = 3 and C(sat, on) = 4.
- The probabilities were right: P(cat | the) = 3/12.
- Sampling was **weighted** by probability. It was not `random.choice`, which would
  have picked each possible next word equally often and ignored the model.
- Every row summed to 1.

## Prompt 2: two generation modes (Part X)

> Modify the program so that it supports two modes. Mode A, greedy: always choose
> argmax_w P(w | w_previous). Mode B, sampling: sample from P(w | w_previous).

**What came back:** `generate()` got a `mode` argument. This is the loop it
produced:

```python
def generate(self, mode="sample"):
    tokens = ["<START>"]
    while tokens[-1] != "<END>":
        if mode == "greedy":
            tokens.append(self.predict(tokens[-1]))
        else:
            tokens.append(self.sample_next(tokens[-1]))
    return " ".join(tokens[1:-1])

def predict(self, prev):
    return max(self.probs[prev], key=self.probs[prev].get)
```

**Two problems were found when this code was run:**

1. **Greedy mode never finishes.** Running it hung, and it was killed after 10
   seconds. Following the table by hand shows why:
   the → cat (0.25, tied with dog) → sat (0.67) → on (1.0) → the → cat → …
   `<END>` is never the most probable next word on this path. So the
   `while tokens[-1] != "<END>"` loop runs forever. Sampling mode does not hang,
   because a random draw eventually picks mat, rug or park, and those lead to `<END>`.
2. **An unseen word crashes the program.** `predict("bird")` raised
   `KeyError: 'bird'`, because `self.probs[prev]` has no row for a word it never
   saw (Question 7).

## Prompt 3: repair

> Greedy generation loops forever on this data (the → cat → sat → on → the …).
> Add a maximum length of 20 words so that generation always stops. For a word
> with no observed transitions, return an empty distribution, make `predict`
> return None, and stop generating instead of crashing. Pass the random
> generator in as an argument so that runs can be repeated exactly. When there
> is a tie, keep the word seen first in training, and say so in a comment.

**What came back:** the current `bigram_model.py`. It adds `MAX_TOKENS = 20`.
`distribution()` now uses `self.probs.get(prev, {})` to handle unseen words.
`generate()` stops at the length cap or at a missing row. `sample_from` and
`most_probable` are split out as helpers, so the second-order model can reuse them.

**Re-checked:** `test_models.py` confirms the following:
- greedy now returns after 20 words;
- `predict("bird")` returns None;
- sampled next words follow the probability table (60,000 draws, all within 0.01);
- sentence frequencies match the chain rule. In 20,000 samples, the share of
  "the park" is within 0.01 of 1 × 2/12 × 1 = 0.167.

## Prompt 4: second-order model (Part XII)

Before this prompt was sent, the changes it should make were written down (the
handout asks for this):

- the table is indexed by **pairs** of previous words, not single words;
- the counts are of **triples** (w_{t-2}, w_{t-1}, w_t);
- each probability is C(a, b, c) / Σ_x C(a, b, x);
- the first two words need a context too, so each sentence starts with **two**
  `<START>` tokens. Then P(X1) is P(X1 | START, START) and P(X2 | X1) is
  P(X2 | START, X1). This is exactly the handout's
  P(X1)P(X2|X1)P(X3|X1,X2)P(X4|X2,X3).

> Modify the existing first-order autoregressive model into a second-order model.
> The model should estimate P(X_t | X_{t-2}, X_{t-1}). Represent the model using
> counts of observed triples and use these counts to construct conditional
> probability distributions. Pad each sentence with two `<START>` tokens. Keep
> the same greedy/sampling modes, the 20-word cap and the unseen-context
> behaviour. Do not replace the model with a neural network or a pretrained
> language model.

**What came back:** `trigram_model.py`.

**Checks:**
- The padding was right. `tokenise2("the cat")` gives
  `[<START>, <START>, the, cat, <END>]`.
- The counts were taken over `zip(tokens, tokens[1:], tokens[2:])`, which is
  triples, as asked.
- Every row sums to 1.
- P(mat | on, the) = 2/4 and P(cat | START, the) = 3/6, as worked out by hand.
- Greedy now reaches `<END>`.

Nothing needed fixing. The reason is that Prompt 4 already stated the padding and
the edge cases that went wrong in Prompts 1 and 2.

---

## Who wrote what

| Part | Written by |
|---|---|
| The model, the questions, the dataset | the handout |
| What to build, including padding, the length cap and unseen words | written down before prompting (the prompts above) |
| `bigram_model.py`, `trigram_model.py` | the LLM, corrected after Prompt 2 |
| `test_models.py`, `run_lab.py` | the LLM, from the handout's Parts VII–XIII |
| Checking every probability against a hand count | done by hand (LAB_REPORT.md §4) |
