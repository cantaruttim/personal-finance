from expenses import build_expenses_report, read_expenses
from installments import build_installments_report, read_installment
from config.config import FILE_PATH_OUTPUT

exp = read_expenses()
inst = read_installment()

print(exp)
