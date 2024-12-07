import requests
from dotenv import dotenv_values
from utils import run_continuously
import time
import schedule
import os
import sqlite3
def get_weather():
    KEY = dotenv_values(os.path.join(os.curdir,'configs','.env'))['KEY']
    URL = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": KEY,
        "city":310114,
        "extended": "base",
        "output": "json"
    }
    try:
        response = requests.get(url=URL, params=params)
        info = response.json()['lives'][0]
        conn = sqlite3.connect(os.path.join(os.curdir,'identifier.sqlite'))
        cursor = conn.cursor()
        cursor.execute('INSERT INTO weather_data (location, description, temperature, timestamp, wind_direction, wind_power, humidity) VALUES (?,?,?,?,?,?,?)',
                       (info['province']+info['city'],info['weather'],info['temperature'],info['reporttime'],info['winddirection'],info['windpower'],info['humidity']))
        conn.commit()
        conn.close()
    except:
        print('max retries exceeded')


if __name__ == '__main__':
    schedule.every(45).minutes.do(get_weather)
    stop_run_continuously = run_continuously()
    time.sleep(60*60*24)
    stop_run_continuously.set()


