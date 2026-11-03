# Company Identity Graph

> 🚧 Work in progress, built in public. Currently at **v0.1 (week 1)**.

A public, continuously updated identity graph of legal entities: the same company resolved across SEC filer IDs (CIK), Legal Entity Identifiers (LEI), tickers and names, with corporate ownership as a graph. Every match carries a measured confidence, and match quality is reported as precision/recall against a labeled set.

## Data sources
- **GLEIF Golden Copy**: LEI entity records (Level 1, ~3.48M as of 2026-10-28) and parent relationships (Level 2)
- **SEC EDGAR**: tickers, submissions, former names (bulk files, fair-access rules respected)

No scraping and no paid data.

## Roadmap
| Version | Scope |
|---|---|
| v0.1 | GLEIF Level 1 → raw layer, one cleaned entity table, data contract and quality checks |
| v0.2 | EDGAR loaded; normalized names and addresses |
| v0.3 | Entity resolution: deterministic, then probabilistic (Splink), with precision/recall on a labeled set |
| v0.4 | Ownership graph with coverage metrics |
| v1.0 | Daily incremental runs, quality gates that block publishing, drift metrics, dashboard |

## Stack
Python · DuckDB · marimo · Splink · dbt · Dagster · PySpark / Databricks (later milestones)

## Repo layout
```
src/company_identity_graph/   pipeline code
notebooks/                    exploration notebooks (marimo, numbered by milestone)
docs/decisions/               decision records
```

## Decisions so far
- [0001 · Local engine: DuckDB](docs/decisions/0001-local-engine.md)
- [0002 · marimo over Jupyter](docs/decisions/0002-marimo-jupyter-comparison.md)

## How this is built
I'm building this with Claude Code as a pair programmer under an explicit working contract ([CLAUDE.md](CLAUDE.md)): I write the core logic (matching, evaluation, graph model, quality gates), and the assistant scaffolds conventional code. Commits that include assistant-written code carry a `Co-Authored-By` trailer.

## Run it
```bash
uv sync
uv run marimo edit notebooks/01_gleif_profile.py
```

## License
MIT
