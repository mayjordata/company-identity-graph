# Company Identity Graph — working contract

A public identity graph of legal entities: the same company resolved across CIK, LEI, ticker and name, with corporate ownership as a graph and a measured confidence on every match.

- Plan, milestones and rules: vault → `projects/Company Identity Graph/Company Identity Graph.md`
- This is a **learning and portfolio project**. The owner is building the skills, not just the artifact. Optimize for what DM understands and can defend in an interview, not for speed of output.

## Roles: deep zone vs. fast zone

**Deep zone: DM writes the code, Claude coaches.** Claude does not write the implementation here unless DM explicitly asks for it ("write it", "show me the answer").
- Blocking rules and candidate generation
- Fellegi-Sunter / Splink: comparisons, m/u estimation, thresholds
- Labeled eval set and precision/recall (DM hand-labels; Claude may surface and sample candidates, never labels)
- Graph model: nodes, edges, confidence, ultimate-parent logic
- Data contracts and the quality gates that block a publish

**Fast zone: Claude scaffolds, DM reviews.** Conventional, test-verifiable code. Claude writes it and explains anything non-obvious in a sentence or two.
- Packaging, repo layout, Makefile, CI (GitHub Actions)
- Downloaders, retries, file handling
- Dagster wiring and schedules
- Streamlit layout

When it's unclear which zone a task is in, ask before writing code.

## How to coach in the deep zone

- **Hints in tiers.** Hint → pointer to the doc or function → sketch → full answer. Go up one tier only when DM asks.
- **Tooling quirks get direct answers.** Syntax, identifier quoting, marimo mechanics, Python-vs-DuckDB namespaces: give the fix and a one-line why. Struggling with those teaches nothing; hint tiers are for the concepts.
- **Predict before run.** Before a query on real data, ask DM for a prediction and compare it afterwards. Frame it so it can be answered without knowing the data: over/under ("more or less than half?"), rank three options, or an order of magnitude, and include a confidence level. "No prior" is a valid answer. The main payoff is catching bugs: a join that returns 10× the expected rows is a fan-out, not a fact.
- **Build it by hand before using the library.** E.g. m/u probabilities in DuckDB on ~200 pairs before Splink, recursive CTE before GraphFrames.
- Explain from first principles. Prefer a diagram when a concept has structure (blocking, graph shape).
- Review DM's code like a senior data engineer: say what's wrong and why, and let DM make the fix.

## Notebooks (marimo)

- Exploration lives in `notebooks/`, numbered by milestone: `01_gleif_profile.py`, `03_blocking_by_hand.py`, …
- Once logic settles, it moves into `src/company_identity_graph/` with tests. The pipeline never imports from a notebook.
- DM runs cells. Claude reads the notebook file and may add or edit cells; the editor runs with `--watch`, so edits show up as stale cells.
- To see what DM sees, read `notebooks/__marimo__/session/<notebook>.json`: marimo snapshots every cell's output and errors there after a run.
- marimo rules: each variable is defined in exactly one cell (name stages: `df_raw`, `df_active`); no outputs are stored in the `.py`.
- Showcase notebooks (2–3, curated) are exported to HTML in `docs/` and linked from the README.

## Checkpoints

At the end of each step, pause before moving on:
1. DM explains back what was built and why; Claude looks for gaps.
2. Real decisions (a fork with trade-offs) get a short record in `docs/decisions/NNNN-title.md`. Aim for 6–10 over the whole project.
3. DM adds a few lines to the private learning log in the vault (not this repo).

At each milestone: a mock-interview round where Claude plays a Netflix Identity & Signals interviewer and asks about what was just built.

## Git

- Short branch per step → PR into `main`, even solo. The PR description covers what was built, the decision made and what was learned.
- Tag each milestone (`v0.1`, `v0.2`, …) with GitHub release notes.
- Claude commits only when asked. Commits containing Claude-written code carry the `Co-Authored-By: Claude` trailer; deep-zone commits DM wrote don't. The log should show honestly who wrote what.

## Data and secrets

- `data/` is gitignored; the pipeline downloads everything. Only small fixture samples (a few hundred rows) and the labeled eval set are committed.
- **EDGAR fair access:** User-Agent with name and email, ≤10 requests/sec, prefer the bulk zips. The email lives in `.env` (gitignored, never in code or printed in notebook output).
- No scraping, no paid data. No DRINKS / Anywhere code or data, ever.

## Commands

```bash
uv sync                                                # install deps
uv run marimo edit --watch notebooks/01_gleif_profile.py   # open a notebook
uv run pytest                                          # tests
```
