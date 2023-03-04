from datetime import date

from utils.functions import *

def process_data():
    today = date.today()
    retroactive_date = get_retroactive_date(today)
    max_month = get_max_month(retroactive_date)
    USD_soup = get_bsoup_object(retroactive_date, tax='PTX')
    EUR_soup = get_bsoup_object(retroactive_date, tax='EUR')

    currencies = get_currencies(soup=USD_soup,
                                tax='PTX',
                                retroactive_date=retroactive_date)
    currency_eur = get_currencies(soup=EUR_soup,
                                  tax='EUR',
                                  retroactive_date=retroactive_date)

    currencies['eur_brl'] = currency_eur['eur_brl']
    currencies = filter_currencies(currencies, max_month)
    
    return currencies

if __name__ == "__main__":
    process_data()