SELECT
    category,
    month,
    COUNT(*) AS total_records

FROM {{ ref('fct_expenses') }}

GROUP BY
    category,
    month

HAVING COUNT(*) > 1