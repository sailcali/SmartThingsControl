import requests
from keys import ENPHASE_TOKEN, ENPHASE_USER_ID, SYSTEM_ID
from datetime import datetime, timedelta
import pandas as pd

pd.set_option("display.max_rows", None, "display.max_columns", None)

SYSTEM_URL = f"https://api.enphaseenergy.com/api/v2/systems?key={ENPHASE_TOKEN}&user_id={ENPHASE_USER_ID}"
PRODUCTION_URL = f'https://api.enphaseenergy.com/api/v2/systems/{SYSTEM_ID}/rgm_stats'


def get_system_data():
    data = requests.get(SYSTEM_URL).json()['systems'][0]

    for key in data.keys():
        print(f"{key}: {data[key]}")


def get_production_data_from_previous_week():
    data = pd.DataFrame(columns=['end_time', 'production'])
    end_date = datetime.today()
    start_date = datetime.today() - timedelta(days=7)
    payload = {'key': ENPHASE_TOKEN, 'user_id': ENPHASE_USER_ID,
               'start_at': start_date.timestamp(), 'end_at': end_date.timestamp()}
    response = requests.get(PRODUCTION_URL, payload)
    body = response.json()
    devices = body.get('total_devices')
    for m in range(devices):
        for interval in body.get('meter_intervals')[m].get('intervals'):
            if interval['channel'] != 1:
                break
            data = data.append({'end_time': datetime.fromtimestamp(interval['end_at']), 'production': interval['curr_w']}, ignore_index=True)
    return data

if __name__ == '__main__':
    weekly_production = get_production_data_from_previous_week()
