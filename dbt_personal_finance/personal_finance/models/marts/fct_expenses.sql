SELECT
    category,
    month,
    amount

FROM {{ ref('int_expenses_unpivoted') }}