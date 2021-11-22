import requests
from keys import ENPHASE_DB_STRING
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

pd.set_option("display.max_rows", None, "display.max_columns", None)

def get_production_data():
    db = create_engine(ENPHASE_DB_STRING)
    data = pd.read_sql_table('production', db)
    return data


def get_select_production_data(start_date, end_date):
    db = create_engine(ENPHASE_DB_STRING)
    with db.connect() as con:
        sql = f"""SELECT * FROM production WHERE time > '{start_date}' AND time < '{end_date}';"""
        result = con.execute(sql)
        data = pd.DataFrame(result.fetchall(), columns=['time', 'production'])
        data.set_index(['time'], inplace=True)
    return data


def get_dates_from_user():
    while True:
        start_date = input('Please enter a start date')
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            my_time = datetime.min.time()
            start_datetime = datetime.combine(start_date, my_time)
            break
        except ValueError:
            print('Please use date format YYYY-MM-DD')

    while True:
        end_date = input('Please enter an end date')
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date + timedelta(days=1)  # We want to include the date the user enters
            my_time = datetime.min.time()
            end_datetime = datetime.combine(end_date, my_time)
            break
        except ValueError:
            print('Please use date format YYYY-MM-DD')
    return start_datetime, end_datetime


def get_user_option():
    options = {1: 'Get Production by Dates', 2: 'Get All Production',
               3: 'Get Top 30 All Time Production Periods'}
    for num in options:
        print(f'{num}. {options[num]}')
    option = int(input('Select and option:\n'))
    return option


if __name__ == '__main__':
    option = get_user_option()
    if option == 1:  # Select production data by date range
        start_date, end_date = get_dates_from_user()
        production = get_select_production_data(start_date, end_date)
        print(production)
    elif option == 2:  # All production data
        all_production = get_production_data()
    elif option == 3:  # top 3 all time production periods (sorted by date)
        all_production = get_production_data()
        all_production['time'] = pd.to_datetime(all_production['time']).dt.date
        unique_production = all_production.sort_values(['production'], ascending=False).drop_duplicates(['time'])
        prod = unique_production.head(30)
        prod.sort_values(['time'], inplace=True)
        print(prod)

