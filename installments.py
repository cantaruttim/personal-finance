import pandas as pd
from config.config import FILE_PATH_INSTALL

install = pd.read_excel(FILE_PATH_INSTALL , 'installments')

print(install.info())