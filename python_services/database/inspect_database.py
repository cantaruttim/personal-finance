from pathlib import Path
import duckdb


BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_PATH = BASE_DIR / "warehouse" / "personal_finance.duckdb"


def inspect_database():

    conn = duckdb.connect(str(DATABASE_PATH))

    print("\n=== TABLES AND VIEWS ===")

    print(
        conn.sql("""
            SELECT
                table_schema,
                table_name,
                table_type
            FROM information_schema.tables
            WHERE table_schema = 'main'
            ORDER BY table_name
        """)
    )

    print("\n=== RAW EXPENSES ===")

    print(
        conn.sql("""
            SELECT *
            FROM raw_expenses
            LIMIT 5
        """)
    )

    print("\n=== STAGING EXPENSES ===")

    print(
        conn.sql("""
            SELECT *
            FROM stg_expenses
            LIMIT 5
        """)
    )

    conn.close()


if __name__ == "__main__":
    inspect_database()