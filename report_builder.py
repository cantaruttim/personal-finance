from utils import (
    total_couple_salary_monthly,
    balance,
    consolidating_salary,
    total_expend_on_month,
    select_columns
)
from month_bill import read_fixed_consumption, consolidated_expenses
from expenses import build_expenses_report, read_expenses
from installments import build_installments_report, read_installment
from config.config import FILE_PATH_OUTPUT
from data.data import (
    SALARY, 
    MONEY_DESIRED_TO_SAVE
)
import pandas as pd

inst = build_installments_report(read_installment())
exp = build_expenses_report(read_expenses())

# def show_exp_and_inst():
#     print("\n Expenses are descrive bellow \n")
#     print(exp)

#     print("\n Installment are descrive bellow \n")
#     print(inst)

salary = total_couple_salary_monthly(SALARY)
exp = consolidating_salary(exp, salary)
exp = balance(exp)


## MONEY DESIRED TO SAVE
exp['should_save'] = (
    exp['total_couple_salary_on_month'] * (MONEY_DESIRED_TO_SAVE / 100)
)
print(exp)

print("\n")
print("Consolidated expenses ... \n")

fixed = read_fixed_consumption()

# exp = balance(exp)
# print(exp)
