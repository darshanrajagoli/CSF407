# Lab Report: Bayesian Networks and Autoregressive Language Models

**CS F407 Artificial Intelligence**

Every number in this report comes from running the code in this folder. Raw
output is in `results.txt`, `test_results.txt` and `generated_sentences.txt`.

```bash
python run_lab.py       # every part of the lab -> results.txt, generated_sentences.txt
python test_models.py   # 26 checks -> test_results.txt  (26 passed, 0 failed)
```

Plain Python 3 only. Nothing to install.

### The seven deliverables (handout §21)

| # | Asked for | Where |
|---|---|---|
| 1 | Python implementation, first-order model | `bigram_model.py` |
| 2 | Python implementation, second-order model | `trigram_model.py` |
| 3 | Conditional probability tables for selected contexts | §4 (first order), §11 (second order) |
| 4 | Examples of generated text | §9, §10, §13, and `generated_sentences.txt` |
| 5 | Probability-normalisation test results | §7, and `test_results.txt` |
| 6 | Answers to Questions 1–14 | §1–§16, one per part |
| 7 | Reflection on LLM use, with corrected code | §17, and `prompts.md` |

---

## 1. Part I: From probability to language

**Question 1. Why is the chain-rule decomposition useful for generating text?**

Choosing a whole sentence in one go means choosing from every possible word
sequence, and there are far too many. The chain rule

P(x₁,…,x_T) = P(x₁) · P(x₂ | x₁) · … · P(x_T | x₁,…,x_{T−1})

lets us build the sentence **one word at a time, left to right**: draw the first
word, then the second given the first, and so on. Each step is one small choice
over the vocabulary. The rule is exact for any distribution, so nothing is lost.
It also gives variable length for free (stop when `<END>` comes out), and every
position in every sentence becomes one "predict the next word" training example.

## 2. Part II: A Bayesian network for text

**Question 2. What independence assumption does X₁ → X₂ → X₃ → X₄ make?**

Given the word just before it, a word is independent of every word before that:

P(X_t | X₁, …, X_{t−1}) = P(X_t | X_{t−1}),  i.e.  X_t ⊥ {X₁,…,X_{t−2}} | X_{t−1}.

This is the **first-order Markov assumption**. In Bayesian-network terms, each
node depends only on its one parent. For example, P(X₄ | X₁, X₂, X₃) = P(X₄ | X₃).

The cost: after "the cat sat on the", the model sees only "the", so "the cat
sat on **the cat** …" is a perfectly acceptable continuation to it (§9).

## 3. Part III: The dataset

The six sentences from the handout (`corpus.txt`), lower-cased, one word per
token. `tokenise()` wraps each one in `<START>`/`<END>`:

```
<START> the cat sat on the mat <END>        <START> the dog ran to the park <END>
<START> the cat sat on the rug <END>        <START> the cat ran to the park <END>
<START> the dog sat on the mat <END>        <START> the dog sat on the rug <END>
```

The vocabulary has 10 words: cat, dog, mat, on, park, ran, rug, sat, the, to.
There are 6 × 7 = 42 transitions.

## 4. Part IV: The conditional probability table

P(w_j | w_i) = C(w_i, w_j) / Σ_k C(w_i, w_k). The full table is below.
Rows are the current word, columns are the next word, and a blank cell means 0.

| current ↓ / next → | the | cat | dog | sat | ran | on | to | mat | rug | park | `<END>` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `<START>` | **6/6** | | | | | | | | | | |
| the | | **3/12** | **3/12** | | | | | 2/12 | 2/12 | 2/12 | |
| cat | | | | **2/3** | 1/3 | | | | | | |
| dog | | | | **2/3** | 1/3 | | | | | | |
| sat | | | | | | **4/4** | | | | | |
| ran | | | | | | | **2/2** | | | | |
| on | **4/4** | | | | | | | | | | |
| to | **2/2** | | | | | | | | | | |
| mat | | | | | | | | | | | **2/2** |
| rug | | | | | | | | | | | **2/2** |
| park | | | | | | | | | | | **2/2** |

**Question 3.** The five contexts the question asks for:

| Context | Next-word distribution | Zero-probability next words |
|---|---|---|
| the | cat 0.25, dog 0.25, mat 0.167, rug 0.167, park 0.167 | the, sat, ran, on, to, `<END>` |
| cat | sat 0.667, ran 0.333 | everything else (9) |
| dog | sat 0.667, ran 0.333 | everything else (9) |
| sat | on 1.0 | everything else (10) |
| ran | to 1.0 | everything else (10) |

The whole table has 121 cells: 17 non-zero and **104 zero**. Some zeros are
sensible ("sat sat" should never happen). Others are just missing data: "the cat
ran on the mat" is good English but gets probability 0, because "ran on" never
appears in the data.

## 5. Part V: Asking the LLM

We gave the LLM a behavioural specification, not "write a language model". The
exact prompts, and what came back each time, are in `prompts.md`.

## 6. Part VI: Inspecting the generated code (`bigram_model.py`)

**Question 4. Where are the transition counts stored?**
In `self.counts`, a nested dictionary: `self.counts[prev][next]` is how many
times `next` followed `prev`. It is filled in `train()`, at line 54
(`self.counts[prev][nxt] += 1`).

**Question 5. Where is P(X_t | X_{t−1}) computed?**
In `train()`, at lines 55–57. Each count is divided by its row total, and the
result goes into `self.probs[prev][next]`. That dictionary *is* the probability
table. Everything else reads it through `distribution()` (line 62).

**Question 6. How does the program choose the next word?**
It can do either, depending on `mode`:

- `mode="greedy"` always takes the **most probable** word, using
  `most_probable`: `max(dist, key=dist.get)` (line 40);
- `mode="sample"` **samples**, using `sample_from`:
  `rng.choices(words, weights=...)` (line 35).

The difference: greedy is deterministic and gives the same sentence every time;
it throws away everything but the top choice. Sampling picks each word *in
proportion to* its probability ("cat" after "the" 25 % of the time, "park"
16.7 %), so only sampling reproduces the distribution the model learned.
`test_models.py` checks this: over 60,000 draws, sampled frequencies after "the"
are within 0.01 of the table.

**Question 7. What happens with a word that has no observed transitions?**
It depends on the version of the code:

- **The LLM's first version crashed** with `KeyError: 'bird'`, because
  `self.probs['bird']` doesn't exist.
- **The corrected version** handles it. `distribution()` returns `{}`,
  `predict()` returns `None`, and `generate()` stops.

With pure counting, an unseen word gets **no distribution at all** and an unseen
transition gets probability **exactly 0**, so the model can't tell "impossible"
from "not seen yet". Real systems fix this with *smoothing* (e.g. add-one) or
*back-off* to a shorter context; we left it out because the handout asks for
estimates from counts. (Generating from `<START>` never hits this case: every
word the model can produce was seen with a successor, even if only `<END>`.)

## 7. Part VII: Testing the probability model

For every context w, Σ_v P(v | w) must equal 1. Result (`results.txt`):

| Model | Contexts checked | Rows summing to 1 |
|---|---|---|
| first-order | 11 | **11 / 11** |
| second-order | 15 | **15 / 15** |

`test_models.py` has 26 checks, all passing. Besides normalisation it checks the
counts against hand counts, the handout's 3/5 and 2/5 example, that sampled
frequencies match the table, that sentence frequencies match the chain rule
("the park" should come out 1 × 2/12 × 1 = 16.7 % of the time; in 20,000 samples
it does, within 0.01), and that the test itself catches a broken table.

**Question 8. What does a total of 0.87 tell you?**
The implementation is **wrong**: that row is not a probability distribution,
and 13 % of the probability has gone missing. Likely causes:
- a divide-by-the-wrong-total bug (for example, dividing by how often the word
  appears anywhere, not by how often it has a next word);
- a next word lost from the row while the total still counts it (for example,
  `<END>` skipped when the table is built);
- smoothing that was applied to some cells and not others.

It is dangerous because **you can't see it in the output**: `random.choices`
quietly rescales its weights, so a 0.87 row still produces sensible sentences,
just from the wrong distribution. Only the sum-to-1 check catches it. (A total
above 1 would mean double counting.)

## 8. Part VIII: Predicting the next word

| Context | P(next \| context) | argmax |
|---|---|---|
| `<START>` | the 1.0 | the |
| the | cat 0.25, dog 0.25, mat/rug/park 0.167 each | **cat (tied with dog)** |
| cat | sat 0.667, ran 0.333 | sat |
| dog | sat 0.667, ran 0.333 | sat |
| sat | on 1.0 | on |
| ran | to 1.0 | to |
| on | the 1.0 | the |
| to | the 1.0 | the |
| mat | `<END>` 1.0 | `<END>` |
| bird (never seen) | no row in the table | `None` |

**Question 9. Are the predictions what you would expect?**
**Some are and some are not.** Short-range patterns match human expectation well:
"sat → on", "ran → to", "on → the". Three places differ:

- **After "the", the model gives mat, rug and park 1/6 each, and each of those
  is always followed by `<END>`.** So half of everything it generates is a
  two-word "sentence": "the mat", "the rug" or "the park". No training sentence
  is two words long, and no person would say one. The model doesn't know where
  in the sentence it is.
- **The answer after "the" is a tie.** "cat" wins only because it came first in
  the data. A person would call cat and dog equally good, and so does the model.
  The "single best word" in this case is arbitrary.
- **After "the cat sat on the", the model is happy with "cat".** A person knows
  from the start of the sentence that a place is coming.

What this shows: the model knows only **how often word pairs occurred in six
sentences**, nothing about meaning, grammar, or anything more than one word
back. A person draws on the whole sentence, world knowledge and far more text.
When the model "sounds wrong", it is not miscounting; it is faithfully reporting
a very narrow view of the data.

## 9. Part IX: Generating text

X₁ ~ P(X₁ | `<START>`), then X₂ ~ P(X₂ | X₁), and so on until `<END>`. Here are the
20 sentences (seed 1, saved in `generated_sentences.txt`):

```
 1. the park
 2. the rug
 3. the dog sat on the rug   (*)
 4. the rug
 5. the park
 6. the cat sat on the cat sat on the rug
 7. the cat sat on the cat ran to the cat ran to the mat
 8. the park
 9. the dog sat on the park
10. the cat sat on the cat sat on the mat
11. the dog sat on the cat sat on the dog sat on the park
12. the park
13. the park
14. the mat
15. the cat ran to the dog ran to the rug
16. the rug
17. the rug
18. the rug
19. the rug
20. the cat sat on the dog ran to the dog sat on the dog sat on the mat
```

(*) is the only one of the 20 that appears in the training data. 11 of the 20 are
distinct.

## 10. Part X: Greedy vs sampling

| Mode A, greedy (×5) | Mode B, sampling (×5, seed 2) |
|---|---|
| the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on | the park |
| *(identical)* | the park |
| *(identical)* | the mat |
| *(identical)* | the rug |
| *(identical)* | the mat |

**Question 10. Which mode gives more variation, and why?**
**Sampling:** 3 distinct sentences out of 5 against 1 out of 5 for greedy (and
177 distinct in 1,000 samples). Greedy is a deterministic function of the table,
so it can only ever produce one sentence. Sampling makes a fresh random choice at
every step, so each run can take a different path.

Greedy has a worse problem here: **it never finishes.** Its path the → cat → sat
→ on → the → … is a cycle, and `<END>` is never the top choice on it; it stops
only because of the 20-word cap (the LLM's first version had no cap and hung,
§17). So the most probable *next word* does **not** give the most probable
*sentence*: the most probable sentences are "the mat", "the rug" and "the park"
(1/6 each), and greedy never produces any of them.

## 11. Part XI: A second-order Bayesian network

P(X_t | X_{t−2}, X_{t−1}), where each word has two parents: X_{t−2} → X_t ← X_{t−1}.
Each sentence is padded with two `<START>` tokens, so P(X₁) = P(X₁ | S, S) and
P(X₂ | X₁) = P(X₂ | S, X₁).

This is the complete second-order table. These are the only 15 contexts ever seen:

| Context (X_{t−2}, X_{t−1}) | Next word |
|---|---|
| (`<START>`, `<START>`) | the 6/6 |
| (`<START>`, the) | cat 3/6, dog 3/6 |
| (the, cat) | sat 2/3, ran 1/3 |
| (the, dog) | sat 2/3, ran 1/3 |
| (cat, sat), (dog, sat) | on 2/2 |
| (cat, ran), (dog, ran) | to 1/1 |
| (sat, on) | the 4/4 |
| (ran, to) | the 2/2 |
| (on, the) | **mat 2/4, rug 2/4** |
| (to, the) | **park 2/2** |
| (the, mat), (the, rug), (the, park) | `<END>` 1.0 |

The extra word of context fixes the problem with "the": after "on the" only mat
and rug are possible (0.5 each), after "to the" only park (1.0). The first-order
model gave each of these 1/6, and gave "cat" 1/4.

**Question 11. How does the second-order model differ?**

| | First-order | Second-order |
|---|---|---|
| 1. Graph | one parent per word (a chain) | two parents per word |
| 2. Probability table | 11 rows, one per previous word: 121 cells, 110 free parameters | 111 rows, one per previous *pair*: 1,221 cells, 1,110 free parameters |
| 3. Context | 1 word | 2 words |
| 4. Data needed | 11 contexts to fill; all 11 were seen | 111 contexts to fill (about V = 10 times more); only 15 seen, 96 have **no data at all** |

(Free parameters are 10 per row, not 11, because each row must add up to 1.)

## 12. Part XII: Using the LLM again

Before accepting any code, we wrote down what should change in the
probabilistic model (also in `prompts.md`, Prompt 4):

1. the table is indexed by **pairs** of previous words, not single words;
2. the counts are of **triples** (w_{t−2}, w_{t−1}, w_t);
3. each probability is C(a, b, c) / Σ_x C(a, b, x), so each row still sums to 1;
4. each sentence starts with **two** `<START>` tokens, so that
   P(X₁) = P(X₁ | S, S) and P(X₂ | X₁) = P(X₂ | S, X₁).

The code that came back was inspected and tested against these four points and
against hand counts. No corrections were needed, because the prompt already
covered the edge cases that went wrong the first time.

## 13. Part XIII: Comparing the two models

| Measure | First-order | Second-order |
|---|---|---|
| Possible contexts | 11 | 111 |
| Table size (free parameters) | 110 | 1,110 |
| Non-zero probabilities learned | 17 | 19 |
| Contexts never seen (zero-probability contexts) | **0** | **96** |
| Distinct sentences in 1,000 samples | **177** | **6** |
| Samples that are *not* a training sentence | 886 / 1,000 | **0 / 1,000** |
| Greedy output | loops, cut at 20 words | "the cat sat on the mat" |

**Coherence: examples, not just scores.**

- First-order, most common new sentences: "the park" (192 of 1,000), "the mat",
  "the rug", "the dog sat on the park", "the cat ran to the mat". Some are
  fragments, some grammatical but wrong. Long outputs wander: "the cat sat on
  the cat ran to the cat ran to the mat".
- Second-order: "the dog sat on the mat", "the cat sat on the rug", "the dog ran
  to the park". All fully coherent, **because every one is a training
  sentence**: with this little data the model has **memorised** the six
  sentences and can't produce anything new.

So the first-order model is diverse but incoherent; the second-order model is
coherent but just copies its data.

**Question 12. Why can more context help, and why can it hurt?**

**It helps** because the next word really depends on more than one word back:
"on the" leads to mat or rug, "to the" leads to park. The one-word context can't
tell these apart and spreads probability over five words; the two-word context
puts it on the right one or two. More context means sharper conditional
distributions.

**It hurts** because the table grows exponentially with the context: with
vocabulary V and n words of context there are roughly Vⁿ rows. Here that is
11 → 111 rows (121 → 1,221 cells), from the **same 42 training transitions**:
- 96 of the 111 contexts have no data at all;
- most of the seen contexts have 1–4 counts, so their estimates are very noisy;
- anything not seen word-for-word gets probability 0.

With a real vocabulary of 50,000 words, a second-order table would have 2.5
billion rows, which no dataset fills. **More context means lower bias but higher
variance.**

## 14. Part XIV: The connection to modern language models

Modern LLMs use the same factorisation: P(x₁,…,x_T) = Πₜ P(x_t | x₁,…,x_{t−1}),
with P(x₁) read as P(x₁ | `<START>`). They also generate the same way: sample a
token, append it, sample again. What changes is how P(x_t | context) is
represented:

| | This lab | Modern LLM |
|---|---|---|
| Representation | explicit table of counts | neural network |
| Context | fixed, 1 or 2 words | thousands of tokens |
| Learning | counting | gradient descent |
| Unseen contexts | probability 0 | handled, because similar contexts share weights |

A neural network solves the problem from Question 12: instead of one row per
context, it **computes** a distribution from any context and shares what it
learns across similar contexts, so it can use long context without an
impossible amount of data.

## 15. Part XV: Reflection on the role of the LLM

**Question 13. Why is Approach B ("implement P(X_t | X_{t−1}) from transition
counts, with sampling") better than Approach A ("write me a language model")?**

- **Specifying the behaviour.** A could come back as anything: a neural network,
  a call to a pretrained model, a unigram model. None of those would be the
  object this lab is about. B pins down the model, so the output can be checked
  against it.
- **Understanding the representation.** Under B we know what should be there
  before we read the code: a count table and a normalised table. That's how Q4
  and Q5 could be answered by pointing at lines 54–57, and how the two-`<START>`
  padding could be checked in the second model.
- **Validating the implementation.** The LLM's first version ran, printed correct
  probabilities, and generated sensible sampled text, and it still had two bugs
  (§17). Code that runs is not the same as code that is correct.
- **Testing probabilistic invariants.** Rows sum to 1, sampled frequencies match
  the table, and sentence frequencies match the chain rule. These follow from the
  *model*, not from the code, so they can be checked however the code is
  written. They catch bugs that reading the output never shows (Q8).
- **Telling the implementation apart from the model.** The model is
  "P(X_t | X_{t−1}) from counts". The implementation is dicts, `random.choices`
  and a loop. The greedy hang and the tie-breaking by insertion order are
  *implementation* facts, not properties of the model. The zeros for unseen
  transitions are a *model* fact. Knowing which is which tells you whether to
  fix the code or change the model.

## 16. Final question

**Question 14. What did thinking of the language model as a Bayesian network give you?**

1. **A picture of the dependencies.** The arrows X_{t−1} → X_t say exactly what
   each word is allowed to depend on. Going from first to second order is just
   adding one more arrow into each node.
2. **A factorisation of the joint distribution.** The network tells you the
   distribution over whole sentences is a product of one small table per node.
   That turns "model all sentences" into "fill in one table from counts".
3. **A way to reason about independence assumptions.** The first-order network
   *says* X_t ⊥ X_{t−2} | X_{t−1}. That one statement explains why the model
   produces "the cat sat on the cat" and "the mat": it can't see two words back.
4. **A principled method for generation.** Sampling each node from its table,
   given its parents, in order (ancestral sampling), gives an exact sample of a
   whole sentence from the joint distribution. The chain-rule test confirms this:
   the "the park" frequency matches 1 × 2/12 × 1. (The only departure is the
   20-word safety cap, which cuts off about 3 % of first-order samples.)
5. **A way to understand the effect of more context.** More parents means larger
   tables, so more data is needed. That is the whole of Question 12, read
   straight off the graph.
6. **A way to test the implementation against its specification.** Each table row
   is a probability distribution, so it must sum to 1. The network tells you which
   invariants to test.

## 17. How the LLM was used and how its output was checked

The LLM (Claude) wrote the code from the specifications in `prompts.md`. Nothing
was accepted just because it ran; it was checked by:

1. comparing every probability with a hand count (§4);
2. running the normalisation test (§7);
3. checking that sampled frequencies and whole-sentence frequencies match the
   model (`test_models.py`);
4. running every mode and edge case, not just the normal path.

**Example of LLM-generated code that was inspected and corrected.** After the
handout's Part X prompt, the LLM produced this loop:

```python
def generate(self, mode="sample"):
    tokens = ["<START>"]
    while tokens[-1] != "<END>":
        if mode == "greedy":
            tokens.append(self.predict(tokens[-1]))
        ...
```

Sampling mode worked. Greedy mode **ran forever** and had to be killed after
10 seconds: following the table by hand, the → cat → sat → on → the is a cycle
and `<END>` is never the most probable word on it. The same code also crashed
with `KeyError` on an unseen word, because it used `self.probs[prev]`.

The fix, in the current `bigram_model.py`:
- a 20-word cap (`MAX_TOKENS`);
- `self.probs.get(prev, {})` for unseen words;
- stopping cleanly when a row is missing.

Tests now cover the cap and the unseen word. Neither bug shows up on the normal
path: sampling from `<START>` never hits either one.

**What we took from this:** the LLM wrote exactly what was asked. Both bugs were
in cases **the prompt didn't mention** (greedy when `<END>` never wins, and an
unknown word). The Part XII prompt spelled those out, and the second-order code
needed no fixes.
