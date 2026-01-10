import pandas as pd
from data.data import (
    TENTH,
    MONEY_DESIRED_TO_SAVE,
    salary
)

def normalize_yearmonth(df):
    '''
        Force yearmonth treatment column in order to keep data with 6 digits
    '''

    df = df.copy()
    df['yearmonth'] = df['yearmonth'].astype(str).str.zfill(6)
    return df

def parse_ptbr_money(series: pd.Series, force_ptbr=False) -> pd.Series:
    s = series.copy()

    if force_ptbr:
        s = (
            s.astype(str)
            .str.strip()
            .str.replace('R$', '', regex=False)
            .str.replace(' ', '', regex=False)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
        )
        return pd.to_numeric(s, errors='coerce')

    if pd.api.types.is_numeric_dtype(s):
        return s.astype(float)

    return (
        s.astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )

def total_expend_on_month(
        df: pd.DataFrame,
        categorical,
        numerical
    ):
    '''
        Total amount of expenses
        Group by data based on YEARMONTH column
    '''
    df = df.copy()
    df['total_expend_on_month'] = (
        df
        .groupby(categorical)[numerical]
        .transform('sum')
    )
    return df

def tenth_(MATH_SALARY, GABI_SALARY, TENTH):
    '''return the tenth of the month'''
    tenth = (MATH_SALARY + GABI_SALARY) * TENTH
    tenth = float(tenth)
    return tenth

def money_to_save(MATH_SALARY, GABI_SALARY, MONEY_DESIRED_TO_SAVE):
    '''return the total money that should be saved'''
    total = (MATH_SALARY + GABI_SALARY) * MONEY_DESIRED_TO_SAVE
    total = float(total)
    return total

def cards_owners(FILE_PATH, SHEET_NAME):
    '''
    Function that is responsible to find the cards owners
    on installments based on the expensive data and cards available

    '''
    df = pd.read_excel( FILE_PATH, SHEET_NAME)
    return (
        df[['card', 'owner']]
        .drop_duplicates()
        .reset_index(drop=True)
    )

def select_columns(df, columns):
    return df[columns]

def total_couple_salary(salary):
    '''
        Returns the total couple`s salary amount
    '''
    salary = pd.DataFrame(salary)
    salary["total_on_month"] = (
        salary["MATHEUS"] + 
        salary["GABRIELLA"]
    )
    salary = salary.sort_values(by='yearmonth', ascending=True)

    salary = select_columns(
        salary, 
        ['yearmonth', 'total_on_month']
    )

    return salary