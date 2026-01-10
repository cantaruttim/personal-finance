from utils import (
    total_couple_salary_monthly,
    balance,
    consolidating_salary
)
from expenses import build_expenses_report, read_expenses
from installments import build_installments_report, read_installment
from config.config import FILE_PATH_OUTPUT
from data.data import salary
import pandas as pd

inst = build_installments_report(read_installment())
exp = build_expenses_report(read_expenses())

def show_exp_and_inst():
    print("\n Expenses are descrive bellow \n")
    print(exp)

    print("\n Installment are descrive bellow \n")
    print(inst)

salary = total_couple_salary_monthly(salary)
exp = consolidating_salary(exp, salary)
exp = balance(exp)

print(exp)


# exp = balance(exp)
# print(exp)

