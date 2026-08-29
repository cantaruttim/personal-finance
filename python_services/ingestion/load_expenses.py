from pathlib import Path
import csv
import sqlite3


BASE_DIR = Path(__file__).resolve().parents[2]
print(f"Base directory: {BASE_DIR}")

CSV_PATH = BASE_DIR / "data" / "expenses.csv"
DATABASE_PATH = BASE_DIR / "warehouse" / "personal_finance.db"

print(f"CSV path: {CSV_PATH}")
print(f"Database path: {DATABASE_PATH}")


def load_expenses():

    print("Loading expenses from CSV to SQLite...")

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = sqlite3.connect(DATABASE_PATH)

    cursor = conn.cursor()

    with open(
        CSV_PATH,
        mode="r",
        encoding="mac_roman",
        newline=""
    ) as file:

        reader = csv.reader(
            file,
            delimiter=";"
        )

        rows = list(reader)

    # Primeira linha contém os nomes das colunas
    headers = rows[0]

    # Cria nomes de colunas seguros para SQLite
    columns = [
        f'"{column.strip()}" TEXT'
        for column in headers
    ]

    cursor.execute("DROP TABLE IF EXISTS raw_expenses")

    cursor.execute(
        f"""
        CREATE TABLE raw_expenses (
            {", ".join(columns)}
        )
        """
    )

    placeholders = ", ".join(
        ["?" for _ in headers]
    )

    cursor.executemany(
        f"""
        INSERT INTO raw_expenses
        VALUES ({placeholders})
        """,
        rows[1:]
    )

    conn.commit()

    conn.close()

    print("Expenses loaded successfully.")


if __name__ == "__main__":
    load_expenses()
