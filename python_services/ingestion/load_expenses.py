from pathlib import Path
import duckdb


BASE_DIR = Path(__file__).resolve().parents[2]

CSV_PATH = BASE_DIR / "data" / "expenses.csv"
DATABASE_PATH = BASE_DIR / "warehouse" / "personal_finance.duckdb"


def load_expenses():

    print(f"Base directory: {BASE_DIR}")
    print(f"CSV path: {CSV_PATH}")
    print(f"Database path: {DATABASE_PATH}")

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV file not found: {CSV_PATH}"
        )

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Loading expenses from CSV to DuckDB...")

    conn = duckdb.connect(str(DATABASE_PATH))

    conn.execute("INSTALL encodings")
    conn.execute("LOAD encodings")

    conn.execute(f"""
        CREATE OR REPLACE TABLE raw_expenses AS
        SELECT *
        FROM read_csv(
            '{CSV_PATH}',
            delim=';',
            encoding='mac_roman',
            header=true
        )
    """)

    print("Expenses loaded successfully!")

    conn.close()


if __name__ == "__main__":
    load_expenses()