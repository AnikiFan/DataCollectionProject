import os
import threading
import schedule
import sqlite3
import re
import ast
import time
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

def upload_log(log_file_path):
    # 定义正则表达式来匹配日志条目
    log_pattern = re.compile(
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - '  # 时间戳
        r'Sensor_.*? - '  # 传感器名称
        r'INFO - '  # 日志级别
        r'Sensor ID: (\w+), '  # 传感器ID
        r'Sensor Type: (\w+), '  # 传感器类型
        r'Location: (\w+), '  # 位置
        r'Status: (\w+), '  # 状态
        r'Data: ({.*})'  # 数据
    )
    with open(log_file_path, 'r+') as file:
        log_content = file.read()
        log_entries = log_pattern.findall(log_content)
        file.truncate(0)
    conn = sqlite3.connect(os.path.join(os.curdir,'identifier.sqlite'))
    cursor = conn.cursor()
    # 打印解析后的日志条目
    for entry in log_entries:
        timestamp, sensor_id, sensor_type, location,status, data_str = entry
        cursor.execute("INSERT INTO log (sensor_id, time,sensor_type, location ,status, data) VALUES (?,?,?,?,?,?)",(
            sensor_id,timestamp,sensor_type,location,status,data_str
        ))
        conn.commit()
    conn.close()


def evaluate(row):
    sensor_type = row['sensor_type']
    data = row['data']
    if sensor_type in ['Temperature','Pressure','Humidity','Light','Vibration']:
        data = float(data.split(':')[-1])
    elif sensor_type == 'Tilt':
        data = data.split(',')
        TX = float(data[0].split(':')[-1])
        TY = float(data[1].split(':')[-1])
    if sensor_type == 'Temperature':
        if abs(data-25)<15:
            return 'Normal'
        elif abs(data-25)<20:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Pressure':
        if abs(data-200)<150:
            return 'Normal'
        elif abs(data-200)<200:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Humidity':
        if abs(data-50)<30:
            return 'Normal'
        elif abs(data-50)<40:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Light':
        if abs(data-500)<600:
            return 'Normal'
        elif abs(data-500)<800:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Vibration':
        if abs(data-0.5)<0.3:
            return 'Normal'
        elif abs(data-0.5)<0.4:
            return 'Warning'
        else:
            return 'Danger'
    elif sensor_type == 'Tilt':
        if abs(TX)>80 or abs(TY)>80:
            return 'Danger'
        elif abs(TX)>60 or abs(TY)>60:
            return 'Warning'
        else:
            return 'Danger'


