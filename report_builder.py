from utils import (total_couple_salary)
from expenses import build_expenses_report, read_expenses
from installments import build_installments_report, read_installment
from config.config import FILE_PATH_OUTPUT
from data.data import salary

inst = build_installments_report(read_installment())
exp = build_expenses_report(read_expenses())
salary = total_couple_salary(salary)

def show_exp_and_inst():
    print("\n Expenses are descrive bellow \n")
    print(exp)

    print("\n Installment are descrive bellow \n")
    print(inst)

def salary_on_month(exp):
    # merging information
    exp = exp.merge(
        salary, 
        on='yearmonth', 
        how='left',
        suffixes=('', '_from_salary')
    )
    return exp

exp = salary_on_month(exp)
print(exp)