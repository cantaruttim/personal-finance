from utils import (
    total_couple_salary_monthly,
    balance,
    consolidating_salary,
    select_columns,
    fill_nan_with_zero
)
from expenses import build_expenses_report, read_expenses, month_expenses_variation
from installments import build_installments_report, read_installment
from config.config import FILE_PATH_OUTPUT
from data.data import (
    SALARY, 
    MONEY_DESIRED_TO_SAVE
)
import pandas as pd

# global variables
value = month_expenses_variation()

# files
inst = build_installments_report(read_installment())
exp = build_expenses_report(read_expenses())

# initial treatments
salary = total_couple_salary_monthly(SALARY)
exp = consolidating_salary(exp, salary)
exp = balance(exp)


## MONEY DESIRED TO SAVE
exp['should_save'] = (
    exp['total_couple_salary_on_month'] * (MONEY_DESIRED_TO_SAVE / 100)
)

exp = fill_nan_with_zero(
    select_columns(
        exp,
        [
            "card",
            "card_flag",
            "owner",
            "yearmonth",
            "total_expend_on_month",
            "should_save"
        ]
    )
)

exp = fill_nan_with_zero(
    exp
        .merge(
            select_columns(
                value, 
                ["yearmonth", "variation_percent"]
            ), 
            on="yearmonth", 
            how='left',
            suffixes=('', '_from_value')
        )
)

print(exp)