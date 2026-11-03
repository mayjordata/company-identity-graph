# 0002 · marimo vs jupyter tool comparison

**Date:** 2026-10-28
**Status:** Decided
**Milestone:** v0.1

## Context
Exploration notebooks will live in a public repo, be edited alongside an AI assistant, and query multi-million-row data. marimo is a newer, reactive alternative to Jupyter, and I wanted to test whether ti fits this kind of project.

## Options considered
a. Jupyter notebook + `nbstripout` / `jupytext`
b. Plain .py scripts with VS Code # %% cells.
c. Databricks notebooks where Spark can live.

## Decision
I ultimately decided to go with marimo for a few reasons:
1. Given that I am working with AI in parallel, that can be advantageous. marimo notebooks `.py` are plain Python. Git diffs are readable, AI edits apply cleanly, and no data or secrets can leak in through stored outputs. Jupyter’s `.ipynb` is JSON that mixes code and outputs.
2. It contains built-in SQL cells that run on DuckDB, which is the local engine I decided to work with.
3. There is no hidden state. Running top to bottom always give me a consistent notebook. That’s a reproducibility property, and it’s the main thing marimo offers over Jupyter.


## Trade-offs
Familiarity is honestly the main thing that I'm giving up, along with adoption and learning a new tool, despite needing to work on the project and focus attention there. Honestly, this is probably a good time to learn too, because working through a project, to me, is typically the best way to learn, even though it may seem slow. The one-definition rule, there are no rendered outputs on GitHub resulting in me needing to export notebooks to HTML, its a smaller ecosystem, and most employers use Jupyter-style notebooks.

Here is an example of the one definition rule. Marimo only allows a variable to be defined in only one cell. 

```
# Jupyter habit, which marimo rejects:
df = load_gleif()          # cell 1
df = df[df.status == "ACTIVE"]   # cell 2: error, `df` is already defined in cell 1

# marimo style:
df_raw = load_gleif()
df_active = df_raw[df_raw.status == "ACTIVE"]
```

## Revisit if...
* If marimo friction costs more than about a half a day by the end of week 1 (things like the one variable definition rule or the reactivity model)
* When Spark work moves to Databricks notebooks (week 5), I will re-evaluate.
* If Splink’s charts don’t render in marimo.
