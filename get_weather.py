import requests
from dotenv import dotenv_values
import threading
import time
import schedule
def get_weather():
    KEY = dotenv_values('.env')['KEY']
    URL = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": KEY,
        "city":310114,
        "extended": "base",
        "output": "json"
    }
    response = requests.get(url=URL, params=params)
    info = response.json()['lives'][0]
    print(info)

def run_continuously(interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


if __name__ == '__main__':
    schedule.every().second.do(get_weather)
    stop_run_continuously = run_continuously()
    time.sleep(10)
    stop_run_continuously.set()


