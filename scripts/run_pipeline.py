"""Validate sources, load DuckDB, run dbt, validate marts, and export CSVs."""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import duckdb
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "src"))
from ingest import SOURCES, ingest  # noqa: E402
from ingest import SOURCE_FILES  # noqa: E402

REQUIRED = {
    "projects": ["project_id", "project_name", "area_m2", "start_date", "planned_end_date"],
    "work_packages": ["work_package_id", "project_id", "work_package_name"],
    "boq": ["boq_line_id", "work_package_id", "quantity", "unit_rate", "budget_amount"],
    "purchases": ["purchase_id", "work_package_id", "supplier_id", "order_amount", "invoiced_amount"],
    "valuations": ["valuation_id", "work_package_id", "certification_date", "certified_amount"],
    "payments": ["payment_id", "valuation_id", "payment_date", "paid_amount"],
    "variations": ["variation_id", "work_package_id", "status", "amount"],
}
KEYS = {"projects": "project_id", "work_packages": "work_package_id", "boq": "boq_line_id",
        "purchases": "purchase_id", "valuations": "valuation_id", "payments": "payment_id",
        "variations": "variation_id"}
NUMERIC = {
    "boq": ["quantity", "unit_rate", "budget_amount"],
    "purchases": ["order_amount", "invoiced_amount"],
    "valuations": ["certified_amount"], "payments": ["paid_amount"],
    "variations": ["amount"], "projects": ["area_m2"],
}


def read_sources() -> dict[str, list[dict[str, str]]]:
    result = {}
    for name in SOURCES:
        path = PROJECT_DIR / "data" / "source" / SOURCE_FILES.get(name, f"{name}.csv")
        if not path.exists():
            raise ValueError(f"Missing source file: {path.relative_to(PROJECT_DIR)}")
        if path.suffix.lower() == ".xlsx":
            frame = pd.read_excel(path, sheet_name=0, dtype=str).fillna("")
            columns = list(frame.columns)
            rows = frame.to_dict(orient="records")
        else:
            with path.open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                columns = reader.fieldnames or []
                rows = list(reader)
        if not columns:
            raise ValueError(f"{path.name} has no header row")
        missing = sorted(set(REQUIRED[name]) - set(columns))
        if missing:
            raise ValueError(f"{path.name} is missing required columns: {', '.join(missing)}")
        if not rows:
            raise ValueError(f"{name}.csv has no data rows")
        for index, row in enumerate(rows, start=2):
            for column in REQUIRED[name]:
                if row.get(column, "").strip() == "":
                    raise ValueError(f"{path.name} row {index}: {column} is blank")
            for column in NUMERIC.get(name, []):
                try:
                    value = float(row[column])
                except (ValueError, TypeError):
                    raise ValueError(f"{path.name} row {index}: {column} must be numeric") from None
                if value < 0:
                    raise ValueError(f"{path.name} row {index}: {column} cannot be negative")
        identifiers = [row[KEYS[name]] for row in rows]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError(f"{path.name} contains duplicate {KEYS[name]} values")
        result[name] = rows
    return result


def validate_references(data: dict[str, list[dict[str, str]]]) -> None:
    def values(table: str, column: str) -> set[str]:
        return {row[column] for row in data[table]}

    checks = [
        ("work_packages", "project_id", "projects", "project_id"),
        ("boq", "work_package_id", "work_packages", "work_package_id"),
        ("purchases", "work_package_id", "work_packages", "work_package_id"),
        ("valuations", "work_package_id", "work_packages", "work_package_id"),
        ("variations", "work_package_id", "work_packages", "work_package_id"),
        ("payments", "valuation_id", "valuations", "valuation_id"),
    ]
    for child, fk, parent, pk in checks:
        unknown = sorted(values(child, fk) - values(parent, pk))
        if unknown:
            raise ValueError(f"{child}.{fk} contains unknown {parent}.{pk}: {', '.join(unknown)}")
    packages = {row["work_package_id"] for row in data["work_packages"]}
    for name in ("boq", "purchases", "valuations", "variations"):
        if values(name, "work_package_id") - packages:
            raise ValueError(f"{name}.work_package_id contains unknown packages")
    valuation_amounts = {r["valuation_id"]: float(r["certified_amount"]) for r in data["valuations"]}
    paid_by_valuation: dict[str, float] = {}
    for row in data["payments"]:
        paid_by_valuation[row["valuation_id"]] = paid_by_valuation.get(row["valuation_id"], 0) + float(row["paid_amount"])
    for key, paid in paid_by_valuation.items():
        if paid > valuation_amounts[key] + 0.01:
            raise ValueError(f"Payments exceed certified amount for valuation {key}")
    for row in data["purchases"]:
        if float(row["invoiced_amount"]) > float(row["order_amount"]) + 0.01:
            raise ValueError(f"Invoiced amount exceeds order amount for purchase {row['purchase_id']}")
    for row in data["boq"]:
        expected = float(row["quantity"]) * float(row["unit_rate"])
        if abs(expected - float(row["budget_amount"])) > 0.01:
            raise ValueError(f"BOQ amount does not reconcile for line {row['boq_line_id']}")


def run_dbt() -> None:
    try:
        from dbt.cli.main import dbtRunner
    except ImportError as exc:
        raise RuntimeError("dbt is not installed. Activate the project environment and run: pip install -r requirements.txt") from exc
    runner = dbtRunner()
    for command in ("run", "test"):
        result = runner.invoke([command, "--project-dir", str(PROJECT_DIR), "--profiles-dir", str(PROJECT_DIR)])
        if not result.success:
            raise RuntimeError(f"dbt {command} failed; review the diagnostic above and correct the source or model.")


def validate_and_export(database: Path) -> None:
    exports = PROJECT_DIR / "exports"
    exports.mkdir(exist_ok=True)
    with duckdb.connect(str(database)) as connection:
        summary = connection.execute("SELECT * FROM mart_project_cost_summary").fetchdf()
        if len(summary) != 1:
            raise ValueError(f"Expected one project summary row, got {len(summary)}")
        row = summary.iloc[0]
        expected_budget = connection.execute("SELECT sum(cast(budget_amount as double)) FROM raw.boq").fetchone()[0]
        expected_actual = connection.execute("SELECT sum(cast(invoiced_amount as double)) FROM raw.purchases").fetchone()[0]
        expected_committed = connection.execute("SELECT sum(cast(order_amount as double)) FROM raw.purchases").fetchone()[0]
        expected_certified = connection.execute("SELECT sum(cast(certified_amount as double)) FROM raw.valuations").fetchone()[0]
        expected_paid = connection.execute("SELECT sum(cast(paid_amount as double)) FROM raw.payments").fetchone()[0]
        for label, observed, expected in (
            ("budget", row.budget_cost, expected_budget),
            ("actual cost", row.actual_cost, expected_actual),
            ("committed cost", row.committed_cost, expected_committed),
            ("certified amount", row.certified_amount, expected_certified),
            ("paid amount", row.paid_amount, expected_paid),
        ):
            if abs(float(observed) - float(expected)) > 0.01:
                raise ValueError(f"Project {label} does not reconcile to its source total")
        for table in ("mart_project_cost_summary", "mart_work_package_costs", "mart_supplier_costs",
                      "mart_variations", "mart_valuation_payments"):
            destination = exports / f"{table}.csv"
            connection.execute(f"SELECT * FROM {table}").fetchdf().to_csv(destination, index=False)
            print(f"Exported {destination.relative_to(PROJECT_DIR)}")
    print("Source and mart reconciliation checks passed.")


def main() -> int:
    try:
        os.chdir(PROJECT_DIR)
        source_data = read_sources()
        validate_references(source_data)
        print("Source checks passed.")
        database = ingest(PROJECT_DIR)
        run_dbt()
        validate_and_export(database)
    except Exception as exc:
        print(f"Pipeline failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
