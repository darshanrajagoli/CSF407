# CS F407 — Laboratory: Transformer Architectures (Machine Translation)

One small working demo for each of the three transformer "shapes", in a single
notebook.

```
.
├── INDEX.md                 <- you are here
├── deliverables/            <- SUBMIT THIS
│   └── transformer_architectures_demo.ipynb
└── explainers/              <- for understanding only (LOCAL ONLY, git-ignored)
    └── explainer.md
```

## `deliverables/`

| Part | Architecture | Task | Model |
|---|---|---|---|
| A | Encoder-Decoder | Machine translation | `facebook/m2m100_418M` |
| B | Decoder-Only | Next-token text generation | `gpt2` |
| C | Encoder-Only | Sentiment classification | `distilbert-base-uncased-finetuned-sst-2-english` |

Run the cells top to bottom, in Google Colab or locally. The first cell
installs everything. The last cell re-runs one example from each part and
prints `PASSED` three times if everything works.

## `explainers/` — local only

This folder is git-ignored. It stays on this computer and is not on GitHub.

| File | What it is |
|---|---|
| `explainer.md` | From zero to the whole picture, with a 📝 Notes box per section: tokens, embeddings, attention, encoder vs decoder, greedy/sampling/beam search (linked to the Bayesian Networks lab), a cell-by-cell walkthrough of each part and the sanity checks, a cheat sheet and likely exam questions |
