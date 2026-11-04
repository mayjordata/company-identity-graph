import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 01 · GLEIF profile (marimo trial run)

    **Goal:** get comfortable with marimo, and take a first look at the shape of a GLEIF Level 1 (LEI) record.

    We use GLEIF's **"last day" delta**: about 83k records updated in the last 24 hours, roughly 2 MB zipped.
    It has the same columns as the 483 MB full golden copy, so it's a cheap way to learn the format before week 1 proper.

    **How this notebook works**
    - The cells above "Your turn" are fast-zone scaffolding: download, load, a column explorer.
    - Everything below "Your turn" is yours.
    - The runtime is **lazy** (set in `pyproject.toml`). Editing a cell marks downstream cells stale instead of rerunning them. Press the run button when you're ready.
    """)
    return


@app.cell
def _():
    import zipfile

    import altair as alt
    import duckdb
    import marimo as mo
    import requests

    return alt, duckdb, mo, requests, zipfile


@app.cell
def _(mo, requests, zipfile):
    # Fast zone: resolve the latest publish, download the "last day" delta once, unzip it.
    _api = "https://goldencopy.gleif.org/api/v2/golden-copies/publishes/latest"
    _meta = requests.get(_api, timeout=30).json()["data"]
    _url = _meta["lei2"]["delta_files"]["LastDay"]["csv"]["url"]

    raw_dir = mo.notebook_dir().parent / "data" / "raw" / "gleif"
    raw_dir.mkdir(parents=True, exist_ok=True)
    _zip_path = raw_dir / _url.rsplit("/", 1)[-1]
    if not _zip_path.exists():
        _resp = requests.get(_url, timeout=120)
        _resp.raise_for_status()
        _zip_path.write_bytes(_resp.content)

    with zipfile.ZipFile(_zip_path) as _zf:
        _csv_name = _zf.namelist()[0]
        _zf.extract(_csv_name, raw_dir)
    csv_path = raw_dir / _csv_name
    publish_date = _meta["publish_date"]

    mo.md(f"Loaded publish **{publish_date}** → `{csv_path.name}`")
    return (csv_path,)


@app.cell
def _(csv_path, duckdb, mo):
    # Raw-layer convention: read every column as text. Typing is the cleaned layer's job,
    # so a malformed date in one record can't break the load.
    con = duckdb.connect()
    con.execute(
        f"CREATE TABLE gleif_delta AS SELECT * FROM read_csv('{csv_path}', header = true, all_varchar = true)"
    )
    _n_rows, _n_cols = con.execute(
        "SELECT (SELECT COUNT(*) FROM gleif_delta), (SELECT COUNT(*) FROM (DESCRIBE gleif_delta))"
    ).fetchone()
    mo.md(f"`gleif_delta`: **{_n_rows:,} rows × {_n_cols} columns**")
    return (con,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Your turn, step 1: predict before you look

    Fill in `my_predictions` **before** you use the column explorer or write any queries. Rough guesses are fine. The gap between your guess and the answer is the lesson.
    """)
    return


@app.cell
def _():
    my_predictions = {
        "pct_active": 65,  # % of records whose entity status is ACTIVE
        "top_jurisdiction": None,  # most common legal jurisdiction
        "pct_with_other_names": 31,  # % of records with at least one other / former name
        "full_file_rows": 5702198,  # rows in the FULL golden copy, not this delta
    }
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 2: explore

    Pick a column to see its top values. This is marimo's reactivity at work: changing the dropdown reruns only the cell below it.
    """)
    return


@app.cell
def _(con, mo):
    _columns = [_row[0] for _row in con.execute("DESCRIBE gleif_delta").fetchall()]
    column_picker = mo.ui.dropdown(options=_columns, label="Column", searchable=True)
    column_picker
    return (column_picker,)


@app.cell
def _(alt, column_picker, con, mo):
    mo.stop(column_picker.value is None, mo.md("_Pick a column above._"))

    _top = con.execute(f"""
        SELECT COALESCE("{column_picker.value}", '∅ null') AS value,
               COUNT(*) AS n,
               ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
        FROM gleif_delta
        GROUP BY 1
        ORDER BY n DESC
        LIMIT 15
    """).df()

    _chart = (
        alt.Chart(_top)
        .mark_bar()
        .encode(x="n:Q", y=alt.Y("value:N", sort="-x", title=None), tooltip=["value", "n", "pct"])
        .properties(height=alt.Step(18))
    )
    mo.hstack([mo.ui.table(_top, selection=None), _chart], widths=[1, 1])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 3: answer your predictions in SQL

    This is a marimo SQL cell running against the `con` DuckDB connection. Add as many SQL cells as you like (the **+** button → SQL).

    Things to work out:
    - Which columns hold the entity status, the jurisdiction and the other names? (Use the explorer.)
    - "At least one other name" may span **several** columns. How do you check them all at once?
    - `full_file_rows` isn't in this data at all. Where would you find it?

    Answers:
    1. % of records whose entity status is ACTIVE: 49,279; 59 percent of the records (I was close at 65, the higher records from the rerun allowed me to get close, I think I would have been wrong when yesterday's 14k delta existed)
    2. most common legal jurisdiction: GB at 32,279; 38.7 percent of the records
    3. % of records with at least one other / former name: 27.2 percent
    4. rows in the FULL golden copy, not this delta: 3,476,696
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            COUNT(*) AS n_records
        FROM
            gleif_delta
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            ROUND(100.0 * AVG(CASE WHEN "Entity.EntityStatus" = 'ACTIVE' THEN 1 ELSE 0 END), 1) AS pct_active
        FROM gleif_delta
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            "Entity.LegalJurisdiction" AS jurisdiction,
            COUNT(*) AS n,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
        FROM gleif_delta
        GROUP BY 1
        ORDER BY n DESC
        LIMIT 10
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            split_part("Entity.LegalJurisdiction", '-', 1) AS country,
            COUNT(*) AS n,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
        FROM gleif_delta
        GROUP BY 1
        ORDER BY n DESC
        LIMIT 10
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            ROUND(100.0 * AVG(CASE WHEN COALESCE(
                "Entity.OtherEntityNames.OtherEntityName.1",
                "Entity.OtherEntityNames.OtherEntityName.2",
                "Entity.OtherEntityNames.OtherEntityName.3",
                "Entity.OtherEntityNames.OtherEntityName.4",
                "Entity.OtherEntityNames.OtherEntityName.5"
            ) IS NOT NULL THEN 1 ELSE 0 END), 1) AS pct_with_other_names
        FROM gleif_delta
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT COUNT(*) AS slot1_empty_but_later_filled
        FROM gleif_delta
        WHERE "Entity.OtherEntityNames.OtherEntityName.1" IS NULL
          AND COALESCE(
              "Entity.OtherEntityNames.OtherEntityName.2",
              "Entity.OtherEntityNames.OtherEntityName.3",
              "Entity.OtherEntityNames.OtherEntityName.4",
              "Entity.OtherEntityNames.OtherEntityName.5"
          ) IS NOT NULL
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT
            "Entity.OtherEntityNames.OtherEntityName.1.type" AS name_type,
            COUNT(*) AS n
        FROM gleif_delta
        WHERE "Entity.OtherEntityNames.OtherEntityName.1" IS NOT NULL
        GROUP BY 1
        ORDER BY n DESC
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT data.lei2.full_file.csv.record_count AS full_file_rows
        FROM read_json_auto('https://goldencopy.gleif.org/api/v2/golden-copies/publishes/latest')
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 4: reflect

    1. Which prediction was furthest off, and why? The total number was the most off and that's mainly because I had no point in reference or prior knowledge, maybe predicting an over/under against an anchored number would have gotten me closer.
    2. This delta only holds records that **changed** in the last day. Is it a fair sample of the full file? What would it over-represent or miss? It's ovserved that 41% of the the delta from today's sample isn't active as well as is dominated by funds, trusts, & GB. I have also seen 2 deltas from 2 days one was 14k sample and today's was 84k so a big swing, I didn't get to see the breakdowns much of yesterdays. A delta over-represents records that change: renewals, lapses, new registrations, and some registration agencies’ bulk processing. It under-represents stable, long-established companies. I mainly would be interested in Large US SEC filers and the data is skewed against the population I would target. Because of this, I do not think it is a fair sample.
    3. Now for question 4, I didn't make a guess because I felt I had no prior knowledge or information so I didn't feel equipped enough to make an educated guess. But I guess in these exercises it at least can serve for an anchor or breadcrumb for me to discover. I did have a bias of the country of USA being near the top but in this delta sample they weren't even in the top 10 which is different than what I would expect.
    5. Write 3 lines in your vault learning log.
    """)
    return


if __name__ == "__main__":
    app.run()
