from pathlib import Path
import duckdb


BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_PATH = BASE_DIR / "warehouse" / "personal_finance.duckdb"


def check_database():

    conn = duckdb.connect(str(DATABASE_PATH))

    print("\n=== TABLES ===")

    print(
        conn.sql("SHOW TABLES")
    )

    print("\n=== RAW EXPENSES ===")

    print(
        conn.sql("""
            SELECT *
            FROM raw_expenses
            LIMIT 5
        """)
    )

    print("\n=== ROW COUNT ===")

    print(
        conn.sql("""
            SELECT COUNT(*) AS total_rows
            FROM raw_expenses
        """)
    )

    conn.close()


if __name__ == "__main__":
    check_database()