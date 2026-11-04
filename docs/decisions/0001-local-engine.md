# 0001 · local engine (DuckDB assessment)

**Date:** 2026-10-28
**Status:** Decided
**Milestone:** v0.1

## Context
Working on a data engineering centric project that includes a data set with 3.48M rows & 338 columns that is nearly all text and about 0.4-2.4% daily changes. The project is a canonical company identity graph that is continuously updated and resolves the same company across identifiers (LEI, CIK, ticker). For local development I want to decide which resource to use, DuckDB, pandas, or other.

## Options considered
1. pandas (typically what I am used to/have used in the past) - this is something I'm familiar with, but wide text data at 3.5M rows would need many GB of memory, and it has no native SQL
2. Polars - fast, but a dataframe API, and Splink doesn't run on it.
3. PySpark - in the target stack, but JVM startup and per-query overhead slow iteration at this size. It comes back in week 5
4. SQLite/Postgres (Also have used in the past) - both store data by the row, which is slow for analytics, and Postgres needs a server running.

## Decision
I am deciding to go with DuckDB for a few reasons:
1. Given I am using Splink in my stack for probabilistic matching, DuckDB can run the same model settings that can later be transferred to Spark or Databricks.
2. The data I am working with is expected to need many GB of memory in pandas (my default & comfortable choice) and is yet not big enough for Spark. I will measure the memory load in pandas when loading the data first week.
3. Zero setup: it's a local analytics database running inside my Python process, with no server, and it queries CSV, Parquet and JSON files directly. In the trial notebook I queried GLEIF's API JSON straight from SQL to get the full-file row count.
4. Using this and marimo in tandem will allow me to have streamlined SQL usage and practice.

## Trade-offs
1. There are slight differences in SQL dialect between DuckDB & Spark, so I need to keep the logic portable.
2. Spark comes later. It's what the target roles ask for, so prototyping on DuckDB delays that practice and risks SQL that doesn't port cleanly.
3. One machine, one writer. DuckDB doesn't scale across machines, and only one process can write to a database file at a time. That will matter once Dagster runs jobs in parallel.
4. Persistence is a separate decision. The trial notebook's database is in memory only, so tables disappear on restart. For the raw layer I still need to choose between Parquet files and a `.duckdb` file.

## Revisit if...
A full pipeline run takes more than 15 minutes on the M4 Pro, the data no longer fits on disk, or Splink comparisons at full scale (3.5M GLEIF records against EDGAR) get too slow to iterate on.
