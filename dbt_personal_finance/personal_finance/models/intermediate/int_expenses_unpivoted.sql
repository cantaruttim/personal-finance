/*

    UNPIVOT raw_expenses
    ON COLUMNS(* EXCLUDE Categories)
    INTO
        NAME month
        VALUE amount


python -c "import duckdb; conn=duckdb.connect('warehouse/personal_finance.duckdb'); print(conn.sql(\"UNPIVOT raw_expenses ON COLUMNS(* EXCLUDE Categories) INTO NAME month VALUE amount LIMIT 10\")); conn.close()"

*/

-- UNPIVOT {{ ref('stg_expenses') }}
-- ON COLUMNS(* EXCLUDE Categories)
-- INTO
--     NAME month
--     VALUE amount

WITH unpivoted AS (

    UNPIVOT {{ ref('stg_expenses') }}
    ON COLUMNS(* EXCLUDE Categories)
    INTO
        NAME month
        VALUE amount

)

SELECT
    Categories AS category,

    CAST(
        month || '-01'
        AS DATE
    ) AS month,

    CASE
        WHEN TRIM(amount) = '-' THEN NULL
        ELSE CAST(
            REPLACE(
                REPLACE(
                    TRIM(amount),'.',''
                ),',','.'
            ) AS DECIMAL(18, 2)
        )
    END AS amount

FROM unpivoted

-- python -c "import duckdb; conn=duckdb.connect('warehouse/personal_finance.duckdb'); print(conn.sql(\"SELECT * FROM int_expenses_unpivoted WHERE amount <> '-' LIMIT 20\")); conn.close()"
-- python -c "import duckdb; conn=duckdb.connect('warehouse/personal_finance.duckdb'); print(conn.sql(\"SELECT * FROM int_expenses_unpivoted WHERE amount <> '-'\")); conn.close()"
-- python -c "import duckdb; conn=duckdb.connect('warehouse/personal_finance.duckdb'); print(conn.sql(\"SELECT DISTINCT '[' || amount || ']' AS valor FROM int_expenses_unpivoted\")); conn.close()"