from pathlib import Path
import duckdb

# python -c "import duckdb; conn=duckdb.connect('warehouse/personal_finance.duckdb'); print(conn.sql('SELECT * FROM int_expenses_unpivoted LIMIT 120')); conn.close()"
BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BASE_DIR / "warehouse" / "personal_finance.duckdb"

def inspect_database():

    conn = duckdb.connect(str(DATABASE_PATH))
    # conn.execute("DROP VIEW IF EXISTS sql_expenses")

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


    print("\n=== INTERMEDIATE LAYER ===")
    print(
        conn.sql("""
            SELECT *
            FROM int_expenses_unpivoted
            LIMIT 25
        """)
    )

    conn.close()


if __name__ == "__main__":
    inspect_database()

# python -c "import duckdb; conn=duckdb.connect('warehouse/personal_finance.duckdb'); print(conn.sql('SELECT * FROM int_expenses_unpivoted WHERE amount IS NOT NULL')); conn.close()"
# python -c "import duckdb; conn=duckdb.connect('warehouse/personal_finance.duckdb'); print(conn.sql('SELECT COUNT(*) AS total, COUNT(amount) AS preenchidos, COUNT(*) - COUNT(amount) AS nulos FROM int_expenses_unpivoted')); conn.close()"