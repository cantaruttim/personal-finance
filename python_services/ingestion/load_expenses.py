from pathlib import Path
import duckdb


BASE_DIR = Path(__file__).resolve().parents[2]
print(f"Base directory: {BASE_DIR}")

CSV_PATH = BASE_DIR / "data" / "expenses.csv"
DATABASE_PATH = BASE_DIR / "warehouse" / "personal_finance.duckdb"

print(f"CSV path: {CSV_PATH}")
print(f"Database path: {DATABASE_PATH}")

def load_expenses():
    print("Loading expenses from CSV to DuckDB...")
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(str(DATABASE_PATH))

    conn.execute(f"""
        CREATE OR REPLACE TABLE raw_expenses AS
        SELECT *
        FROM read_csv('{CSV_PATH}', delim=';', encoding='mac_roman', header=True)
    """)

    conn.close()

    print("Expenses loaded successfully.")


if __name__ == "__main__":
    load_expenses()