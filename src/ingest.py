"""Load the fictional CSV sources into the DuckDB raw schema."""
from pathlib import Path

import duckdb


SOURCES = (
    "projects", "work_packages", "boq", "purchases",
    "valuations", "payments", "variations",
)
SOURCE_FILES = {"boq": "boq.xlsx"}


def ingest(project_dir: Path) -> Path:
    warehouse_dir = project_dir / "warehouse"
    warehouse_dir.mkdir(parents=True, exist_ok=True)
    database = warehouse_dir / "construction_cost.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute("CREATE SCHEMA IF NOT EXISTS raw")
        for table in SOURCES:
            source_path = project_dir / "data" / "source" / SOURCE_FILES.get(table, f"{table}.csv")
            if source_path.suffix.lower() == ".xlsx":
                import pandas as pd
                frame = pd.read_excel(source_path, sheet_name=0)
                connection.register("source_frame", frame)
                connection.execute(f"CREATE OR REPLACE TABLE raw.{table} AS SELECT * FROM source_frame")
                connection.unregister("source_frame")
            else:
                connection.execute(
                    f"CREATE OR REPLACE TABLE raw.{table} AS SELECT * FROM read_csv_auto(?)",
                    [str(source_path)],
                )
            count = connection.execute(f"SELECT count(*) FROM raw.{table}").fetchone()[0]
            print(f"Loaded raw.{table}: {count} rows")
    return database
