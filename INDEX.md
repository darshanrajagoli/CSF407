# CS F407: Artificial Intelligence — Repository Master Index

Comprehensive index and navigation guide for all coursework, lab assignments, project deliverables, and technical reports in **CS F407 (Artificial Intelligence)**.

---

## 🧭 Repository Directory Overview

```
CS F407/
├── INDEX.md                                       <- Repository Master Index (This File)
├── ai_handout_2026-2027_s1.pdf                    <- Course syllabus & policy handout
├── Audio_Engineering_AI_Project_Proposal.docx     <- Term project proposal
│
├── Search Hands-on/                               <- Lab: Search and A* Navigation
│   ├── INDEX.md                                   <- Module index
│   ├── search_lab_ex.pdf                          <- Lab assignment sheet
│   ├── deliverables/                              <- Final code & reports (for submission)
│   │   ├── astar_warehouse.py                     <- A* & BFS agent implementation
│   │   ├── test_search.py                         <- Unit test suite (20 checks)
│   │   ├── experiments.py                         <- Benchmark comparisons & heuristic tests
│   │   ├── LAB_REPORT.md                          <- Comprehensive 9-section lab report
│   │   ├── task0_1_formulation_and_design.md      <- Problem formulation & pre-LLM design
│   │   ├── prompts.md                             <- Appendix of LLM engineering prompts
│   │   ├── results.txt                            <- Output of BFS vs A* & heuristic sweeps
│   │   ├── test_results.txt                       <- Raw output of test suite
│   │   └── warehouse.txt                          <- ASCII map of warehouse
│   └── explainers/                                <- Conceptual deep-dive notes
│       ├── explainer.pdf                          <- 10-page standalone guide
│       └── explainer.tex                          <- LaTeX source
│
├── Logic Hands-on/                                <- Lab: Logical Planning & Prolog Verifier
│   ├── INDEX.md                                   <- Module index
│   ├── logic_lab_ex.pdf                           <- Lab assignment sheet
│   ├── deliverables/                              <- Final code & reports (for submission)
│   │   ├── planner.py                             <- Propositional BFS planning agent
│   │   ├── test_planner.py                        <- Unit test suite (42 checks)
│   │   ├── experiments.py                         <- State-space analysis & defect sweeps
│   │   ├── planner.pl                             <- Declarative warehouse domain facts & rules
│   │   ├── reasoning.pl                           <- Classical Horn-clause inference rules
│   │   ├── prolog_engine.py                       <- SLD-resolution inference engine
│   │   ├── run_prolog.py                          <- Prolog query runner & verifier loop
│   │   ├── LAB_REPORT.md                          <- Comprehensive 10-section lab report
│   │   ├── task0_1_specification_and_plan.md      <- Task 0-1 specs & hand-built plan
│   │   ├── prompts.md                             <- Appendix of LLM engineering prompts
│   │   ├── planner_output.txt                     <- Planner run output & trajectory
│   │   ├── test_results.txt                       <- Raw output of test suite
│   │   ├── results.txt                            <- Output of state-space experiments
│   │   └── prolog_session.txt                     <- Complete Prolog verification transcript
│   └── explainers/                                <- Conceptual deep-dive notes
│       ├── explainer.pdf                          <- 11-page standalone guide
│       └── explainer.tex                          <- LaTeX source
│
└── Labs/                                          <- Staging directory for new laboratory work
    └── Lab_2026-09-16/                            <- Workspace for today's lab session
```

---

## 📚 1. Course Information

- **Course**: CS F407 Artificial Intelligence (3 Credits)
- **Instructors**: Dr. Tirtharaj Dash (CC-107) and Prof. Ashwin Srinivasan (D-167)
- **Handout**: [ai_handout_2026-2027_s1.pdf](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/ai_handout_2026-2027_s1.pdf)
- **Evaluation Components**:
  - Worksheets / Lab Work (best $k$-of-$N$): **20 marks**
  - Comprehensive Exam: **30 marks**
  - Course Project: **30 marks**
  - Paper Reading: **10 marks**
  - Tutorial Participation: **10 marks**

---

## 🔍 2. Search Hands-on (`Search Hands-on/`)

Explores **state-space search, heuristic design, and LLM-assisted code engineering** on a 64-cell warehouse grid obstacle domain.

- **Assignment Handout**: [search_lab_ex.pdf](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Search%20Hands-on/search_lab_ex.pdf)
- **Module Index**: [INDEX.md](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Search%20Hands-on/INDEX.md)
- **Status**: **100% Completed & Verified (20/20 checks passed)**

### Deliverables Breakdown

| Deliverable | Description | File Link |
|---|---|---|
| **Main Lab Report** | Complete 9-section report covering Tasks 0–7 and Final Reflections | [LAB_REPORT.md](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Search%20Hands-on/deliverables/LAB_REPORT.md) |
| **Pre-LLM Design** | Formal formulation $P=(S,A,T,s_0,G,c)$ and agent architecture | [task0_1_formulation_and_design.md](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Search%20Hands-on/deliverables/task0_1_formulation_and_design.md) |
| **A\* Agent** | Python implementation of A\* with tie-breaking, lazy deletion, and BFS | [astar_warehouse.py](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Search%20Hands-on/deliverables/astar_warehouse.py) |
| **Test Suite** | Unit tests covering original map, edge cases, disconnected goals, and detours | [test_search.py](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Search%20Hands-on/deliverables/test_search.py) |
| **Benchmarks** | Empirical comparisons across BFS and 4 heuristics ($h=0$, Manhattan, Euclidean, $2\times\text{Manhattan}$) | [experiments.py](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Search%20Hands-on/deliverables/experiments.py) |
| **Prompt Log** | Verbatim prompts submitted to the LLM assistant | [prompts.md](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Search%20Hands-on/deliverables/prompts.md) |
| **Test Results** | Verified output logs from test executions | [test_results.txt](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Search%20Hands-on/deliverables/test_results.txt) |
| **Experiment Results** | Raw tabular output from algorithm sweeps | [results.txt](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Search%20Hands-on/deliverables/results.txt) |
| **Study Guide** | Standalone 10-page tutorial document | [explainer.pdf](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Search%20Hands-on/explainers/explainer.pdf) |

### Key Findings & Insights
1. **Warehouse Solution**: The optimal path requires **40 moves** (all 64 free cells must be expanded because the warehouse map acts as a single constrained corridor).
2. **The FIFO Tie-Break Trap**: When $f(n)$ ties on a unit-cost grid, FIFO queue ordering reduces A\* to BFS (116 expansions on open grids). Adding a prefer-deeper tie-break ($\max g$) cuts expansions from **116 to 26** without losing optimality.
3. **Inadmissible Heuristics**: $2 \times \text{Manhattan}$ speeds up search on simple maps, but in cluttered environments it sacrifices optimality, yielding a suboptimal path (30 moves vs. optimal 28 moves).

### How to Run
```powershell
cd "Search Hands-on\deliverables"
python astar_warehouse.py    # Run A* on the warehouse map
python test_search.py        # Run test suite (20 tests)
python experiments.py        # Run BFS vs A* comparisons
```

---

## 🧠 3. Logic Hands-on (`Logic Hands-on/`)

Demonstrates the foundational principle: **Logic + Search = Planning**, integrating propositional domain modeling, BFS state-space search, and independent formal verification using Prolog.

- **Assignment Handout**: [logic_lab_ex.pdf](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Logic%20Hands-on/logic_lab_ex.pdf)
- **Module Index**: [INDEX.md](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Logic%20Hands-on/INDEX.md)
- **Status**: **100% Completed & Verified (42/42 checks passed)**

### Deliverables Breakdown

| Deliverable | Description | File Link |
|---|---|---|
| **Main Lab Report** | Complete 10-section report covering Tasks 0–8, §5 Reflections, and §7.2 Prolog Reflections | [LAB_REPORT.md](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Logic%20Hands-on/deliverables/LAB_REPORT.md) |
| **Specification & Plan** | Formal propositional preconditions/effects and manual step-by-step state trace | [task0_1_specification_and_plan.md](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Logic%20Hands-on/deliverables/task0_1_specification_and_plan.md) |
| **Planning Agent** | BFS planner with propositional states, duplicate detection, and execution verifier | [planner.py](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Logic%20Hands-on/deliverables/planner.py) |
| **Test Suite** | Unit tests covering solvable problems, impossible goals, irrelevant actions, and cycle traps | [test_planner.py](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Logic%20Hands-on/deliverables/test_planner.py) |
| **Experiments** | Reachable state-space analysis and demonstration of the three modeling defects | [experiments.py](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Logic%20Hands-on/deliverables/experiments.py) |
| **Prolog Domain Model** | Independent warehouse connectivity facts and `can_move/2`, `valid_move/2` rules | [planner.pl](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Logic%20Hands-on/deliverables/planner.pl) |
| **Prolog Reasoning Rules** | Horn clauses demonstrating classical modus ponens chains | [reasoning.pl](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Logic%20Hands-on/deliverables/reasoning.pl) |
| **SLD Engine** | Pure-Python resolution engine enabling Prolog queries without third-party installs | [prolog_engine.py](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Logic%20Hands-on/deliverables/prolog_engine.py) |
| **Verifier Session** | Python-to-Prolog translation and plan verification loop | [run_prolog.py](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Logic%20Hands-on/deliverables/run_prolog.py) |
| **Study Guide** | Standalone 11-page tutorial document | [explainer.pdf](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Logic%20Hands-on/explainers/explainer.pdf) |

### Key Findings & Insights
1. **Optimal Plan**: Exactly 4 actions:
   $$\text{PickUp}(Package, A) \to \text{Move}(A, B) \to \text{Move}(B, C) \to \text{Drop}(Package, C)$$
2. **Precondition Checks**: If preconditions are ignored, the robot moves to B and tries to pick up a package still at A, producing invalid states where the package is in two locations simultaneously.
3. **Internal vs. External Verification**: An LLM will convincingly explain that an invalid plan (e.g. `Move(A,C)`) is valid because it evaluates the plan against an unconstrained action model. The Prolog verifier catches this because it checks the plan against an independent, ground-truth knowledge base.

### How to Run
```powershell
cd "Logic Hands-on\deliverables"
python planner.py         # Solve the warehouse planning problem
python test_planner.py    # Run test suite (42 tests)
python experiments.py     # Run state-space and defect benchmarks
python run_prolog.py      # Run Prolog queries and external verification
```

---

## 🎙️ 4. Course Project (`Audio_Engineering_AI_Project_Proposal.docx`)

- **Title**: Advanced Computational Speech Engineering
- **File**: [Audio_Engineering_AI_Project_Proposal.docx](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Audio_Engineering_AI_Project_Proposal.docx)
- **Scope**: Building a multi-stage **"Who Spoke What and When"** speech processing pipeline tailored to spontaneous, noisy, code-switched Indian audio environments.
- **Core Technical Pillars**:
  1. *Source Separation*: Isolating overlapping speakers using deep generative models.
  2. *Speaker Diarization*: Unsupervised clustering on localized speaker embeddings.
  3. *Regional ASR*: Low-resource automatic speech recognition for multilingual and code-switched speech.
  4. *LLM Post-Processing*: Transcript cleaning, syntactic structuring, and semantic summarization.

---

## 🧪 5. Labs Staging (`Labs/`)

Dedicated directory for incoming laboratory assignments and worksheets.

- **Today's Lab Workspace**: [Lab_2026-09-16](file:///c:/Users/darsh/OneDrive/Desktop/CS%20F407/Labs/Lab_2026-09-16)
- Ready for receiving prompt sheets, starter codes, or test data.

---

## ⚡ Quick Verification Command Summary

Run all test suites across the repository with a single PowerShell snippet:

```powershell
# Verify Search Lab
python "Search Hands-on\deliverables\test_search.py"

# Verify Logic Lab
python "Logic Hands-on\deliverables\test_planner.py"

# Verify Prolog Logical Verifier
python "Logic Hands-on\deliverables\run_prolog.py"
```
