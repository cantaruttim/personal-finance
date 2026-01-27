import pandas as pd
from datetime import datetime
from data.data import (
    TENTH,
    MONEY_DESIRED_TO_SAVE,
    SALARY,
    DANI_VALUE
)

# ================================================
# ==== USED ON DATA TREATMENTS OR GENERAL USE ====
# ================================================
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

def fill_nan_with_zero(df):
    return df.fillna(0)

def tenth_(MATH_SALARY, GABI_SALARY, TENTH):
    '''return the tenth of the month'''
    tenth = (MATH_SALARY + GABI_SALARY) * TENTH
    tenth = float(tenth)
    return tenth

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


# ================================
# ==== USED ON REPORT_BUILDER ====
# ================================
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

def total_couple_salary_monthly(SALARY):
    salary = pd.DataFrame(SALARY)
    salary = (
        salary
        .assign(total_couple_salary_on_month=(
            salary['MATHEUS'] + 
            salary['GABRIELLA'])
        )
        .groupby('yearmonth', as_index=False)['total_couple_salary_on_month']
        .sum()
    )
    return salary

def consolidating_salary(exp, salary):

    exp = exp.merge(
        salary,
        on='yearmonth',
        how='left',
        suffixes=('', '_from_salary')
    )

    return exp

def balance(exp):
    exp['balance'] = (
        exp['total_expend_on_month'] - 
        exp['total_couple_salary_on_month']
    )
    exp["perc_balance"] = round(
        exp['total_expend_on_month'] /
        exp['total_couple_salary_on_month'],
        4
    )
    return exp


def perc_month_variation(df):
    df['yearmonth'] = df['yearmonth'].astype(str).str.zfill(6)

    df['year'] = df['yearmonth'].str[-4:].astype(int)
    df['month'] = df['yearmonth'].str[:2].astype(int)

    df = df.sort_values(['year', 'month']).reset_index(drop=True)

    df['next_value'] = df.groupby('year')['value'].shift(-1)

    df['variation_percent'] = (
        (df['next_value'] - (df['value'] - DANI_VALUE)) / (df['value'] - DANI_VALUE)
    ) * 100

    df['variation_percent'] = df['variation_percent'].round(2)

    current_year = datetime.now().year
    df = df[df['year'] == current_year].reset_index(drop=True)
    return df
