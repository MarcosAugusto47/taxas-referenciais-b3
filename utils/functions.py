import pandas as pd
import re
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

from dateutil.relativedelta import relativedelta

TAXA_DICT = {'PTX': 'usd_brl', 'EUR': 'eur_brl'}


def get_retroactive_date(today):
    """
    Gets the first day of the current that is not Saturday on Sunday

    Parameters
    ----------
    today: datetime.date object of current day

    Returns
    -------
    retroactive_date: datetime.date object
    """
    
    retroactive_date = today.replace(day=1)
    # 0, 1, 2, 3, 4 corresponds to monday to friday
    while retroactive_date.weekday() %  7 not in [0, 1, 2, 3, 4]:
        retroactive_date = retroactive_date + relativedelta(days=1)

    return retroactive_date


def get_first_day_month(today):
    return today.replace(day=1)


def get_max_month(x):
    max_month = 12
    return (pd.to_datetime(x) + relativedelta(months=max_month)) \
        .strftime('%Y-%m')


def format_date(x):
    """
    Creates two string formats of a datetime.date object 
    """
    x = str(x)
    date1 = re.split('-', x)[::-1]
    date1 = "/".join([item for item in date1])
    date2 = re.sub('-', '', x)

    return date1, date2


def trata_html(input):
    return " ".join(input.split()).replace('> <', '><')


def create_bsoup_object(url):
    req = Request(url)
    response = urlopen(req)
    html = response.read()
    html = html.decode('latin-1')
    html = trata_html(html)
    # create BeautifulSoup object
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_bsoup_object(retroactive_date, tax):
    date1, date2 = format_date(retroactive_date)
    URL = f'https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-taxas-referenciais-bmf-ptBR.asp?Data={date1}&Data1={date2}&slcTaxa={tax}'
    soup = create_bsoup_object(URL)
    return soup


def convert_string_to_float(df, colnames):
    for colname in colnames:
        df[colname] = df[colname].str.replace('[R$]', "", regex=True)
        df[colname] = df[colname].str.replace('.', "", regex=False)
        df[colname] = df[colname].str.replace(',', ".", regex=False)
        df[colname] = df[colname].apply(float)
    return df


def get_currencies(soup, tax, retroactive_date):
    """
    Gets tax of Taxas Referenciais Beautiful Soup object

    Parameters
    ----------
    soup: Taxas Referenciais Beautiful Soup object
    tax: currency USD/BRL or EUR/BRL
    retroactive_date: first day of current month but not Saturday or Sunday

    Returns
    -------
    df: pandas Dataframe

    """

    days = [int(x.get_text()) for x in soup.findAll('td', {'class': ''})]
    price = [x.get_text() for x in soup.findAll('td', {'class': 'text-right'})]

    df = pd.DataFrame({'days': days, TAXA_DICT[tax]: price})
    df = convert_string_to_float(df, [TAXA_DICT[tax]])
    df['date_retroactive'] = retroactive_date
    
    # get month_year from date_retroactive
    df['month_year_reference'] = df['date_retroactive'] \
        .apply(lambda x: x.strftime('%Y-%m'))
    
    # get date after passing days
    df['date_step'] = df \
        .apply(lambda x: x['date_retroactive'] + relativedelta(days=x['days']),
               axis=1)
    df['month_year'] = df['date_step'].apply(lambda x: x.strftime('%Y-%m'))
    
    df['date_retroactive'] = str(retroactive_date)

    return df


def filter_currencies(df, max_month):
    """
    Selects a dataframe by columns and filters only rows before or equal
    to a specific month
    """
    cols = ['days',
            'usd_brl',
            'eur_brl',
            'date_retroactive',
            'month_year']
    df = df[cols]
    df = df[df.month_year <= max_month]

    return df


def month_currency_means(df):
    months_mean = df.groupby(['month_year_reference', 'month_year']) \
        [['usd_brl', 'eur_brl']].mean().reset_index()
    return months_mean
