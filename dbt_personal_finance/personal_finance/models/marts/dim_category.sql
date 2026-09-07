SELECT DISTINCT
    category
FROM {{ ref('int_expenses_unpivoted') }}
WHERE category IS NOT NULL