import time
import random
import sqlite3
import requests
import re
import json
import tkinter as tk
from tkinter import ttk

# 传感器类
class Sensor:
    def __init__(self, sensor_id, sensor_name, sensor_type, sensor_location):
        self.sensor_id = sensor_id
        self.sensor_name = sensor_name
        self.sensor_type = sensor_type
        self.sensor_location = sensor_location

    def collect_data(self):
        if self.sensor_type == 'temperature':  # 温度
            return random.uniform(0, 40)
        elif self.sensor_type == 'humidity':  # 湿度
            return random.uniform(0, 100)
        elif self.sensor_type == 'vibration':  # 震动
            return random.uniform(0, 10)
        elif self.sensor_type == 'acceleration':  # 倾斜-使用加速度传感器替代
            return random.uniform(0, 5)
        elif self.sensor_type == 'deformation':  # 变形
            return random.uniform(0.05, 2)
        elif self.sensor_type == 'stress':  # 压力
            return random.uniform(200, 500)

# 网关设备
class Gateway:
    def __init__(self):
        self.sensors = {
            'vibration': Sensor(1, 'Vibration Sensor 1', 'vibration', '主桥墩'),
            'deformation': Sensor(2, 'Deformation Sensor 1', 'deformation', '桥面'),
            'stress': Sensor(3, 'Stress Sensor 1', 'stress', '桥梁横梁'),
            'temperature': Sensor(4, 'Temperature Sensor 1', 'temperature', '桥面'),
            'humidity': Sensor(5, 'Humidity Sensor 1', 'humidity', '桥面'),
            'acceleration': Sensor(6, 'Acceleration Sensor 1', 'acceleration', '桥面')
        }

    def collect_sensor_data(self):
        data = {}
        for sensor_name, sensor in self.sensors.items():
            value = sensor.collect_data()
            status = self.check_sensor_status(sensor.sensor_type, value)
            data[sensor_name] = {
                'value': value,
                'location': sensor.sensor_location,
                'status': status,
                'type': sensor.sensor_type,
                'name': sensor.sensor_name
            }
        return data

    def check_sensor_status(self, sensor_type, value):
        if sensor_type == 'vibration' and value > 5:
            return 'WARNING'
        elif sensor_type == 'deformation' and value > 1:
            return 'WARNING'
        elif sensor_type == 'stress' and value > 400:
            return 'WARNING'
        elif sensor_type == 'temperature' and (value < 0 or value > 35):
            return 'WARNING'
        elif sensor_type == 'humidity' and (value < 20 or value > 80):
            return 'WARNING'
        elif sensor_type == 'acceleration' and value > 3:
            return 'WARNING'
        else:
            return 'normal'

# 数据库操作
class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id INTEGER,
                sensor_name TEXT,
                value REAL,
                location TEXT,
                status TEXT,
                type TEXT,
                timestamp TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weather TEXT,
                temperature REAL,
                humidity REAL,
                timestamp TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                log_level TEXT,
                log_content TEXT
            )
        ''')
        self.conn.commit()

    def insert_sensor_data(self, sensor_id, sensor_name, value, location, status, sensor_type):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.cursor.execute('''
            INSERT INTO sensor_data (sensor_id, sensor_name, value, location, status, type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sensor_id, sensor_name, value, location, status, sensor_type, timestamp))
        self.conn.commit()

    def insert_weather_data(self, data):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.cursor.execute('''
            INSERT INTO weather_data (weather, temperature, humidity, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (data[0], data[1], data[2], timestamp))
        self.conn.commit()

    def insert_system_log(self, log_level, log_content):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.cursor.execute('''
            INSERT INTO system_logs (timestamp, log_level, log_content)
            VALUES (?, ?, ?)
        ''', (timestamp, log_level, log_content))
        self.conn.commit()

    def get_latest_sensor_data(self):
        self.cursor.execute('''
            SELECT sensor_id, sensor_name, value, location, status, type, timestamp
            FROM sensor_data
            WHERE timestamp = (
                SELECT MAX(timestamp)
                FROM sensor_data
                WHERE sensor_id = sensor_data.sensor_id
            )
        ''')
        return self.cursor.fetchall()

    def get_latest_weather_data(self):
        self.cursor.execute('SELECT * FROM weather_data ORDER BY timestamp DESC LIMIT 1')
        return self.cursor.fetchone()

    def get_latest_system_logs(self):
        self.cursor.execute('SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT 10')
        return self.cursor.fetchall()

    def get_historical_sensor_data(self):
        self.cursor.execute('''
            SELECT sensor_id, sensor_name, value, location, status, type, timestamp
            FROM sensor_data
            ORDER BY timestamp DESC
        ''')
        return self.cursor.fetchall()

city_codes = {
    '北京': '101010100',
    '上海': '101020100',
    '成都': '101270101',
    '嘉定': '101020500',
    # 其他城市代码
}

# 互联网数据获取
def get_weather_from_internet(city):
    if city not in city_codes:
        raise ValueError(f"City code for {city} not found")
    
    city_code = city_codes[city]
    url = f'http://www.weather.com.cn/weather1d/{city_code}.shtml'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    timeout = 10
    response = requests.get(url, headers=headers, stream=True, timeout=timeout)
    
    if response.status_code != 200:
        raise ValueError("Failed to retrieve content")
    
    pattern = re.compile(r'var observe24h_data = (.*?);')
    match = pattern.search(response.text)
    if match:
        json_str = match.group(1)
        data = json.loads(json_str)
        latest_data = data['od']['od2'][0]
        temperature = latest_data['od22']
        windspeed = latest_data['od25']  # 风力等级
        humidity = latest_data['od27']
        return windspeed, temperature, humidity
    else:
        print("未找到温湿度信息")
        return None, None

# 数据整合分析
def integrate_data(db, tree):
    sensor_data = db.get_latest_sensor_data()
    weather_data = db.get_latest_weather_data()
    tree.delete(*tree.get_children())
    for data in sensor_data:
        sensor_id, sensor_name, value, location, status, sensor_type, timestamp = data
        unit = get_unit(sensor_type)
        tree.insert('', 'end', values=(sensor_id, sensor_name, location, f"{value}{unit}", status, timestamp))
    if weather_data:
        weather_id, windspeed, temperature, humidity, timestamp = weather_data
        tree.insert('', 'end', values=('Weather', '', '', f"{windspeed} 级, {temperature} °C, {humidity} %", '', timestamp))

def get_unit(sensor_type):
    units = {
        'temperature': '°C',
        'humidity': '%',
        'vibration': 'mm',
        'acceleration': 'm/s²',
        'deformation': 'cm',
        'stress': 'kPa'
    }
    return units.get(sensor_type, '')

# GUI界面
class App:
    def __init__(self, root, gateway, db, city):
        self.root = root
        self.gateway = gateway
        self.db = db
        self.root.title("桥梁监测系统")
        self.city = city
        self.current_view = "overview"  # 当前视图
        self.create_widgets()
        self.update_data()

    def create_widgets(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.overview_frame = ttk.Frame(self.notebook)
        self.sensor_frame = ttk.Frame(self.notebook)
        self.log_frame = ttk.Frame(self.notebook)
        self.status_frame = ttk.Frame(self.notebook)
        self.history_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.overview_frame, text="数据总览")
        self.notebook.add(self.sensor_frame, text="查看数据")
        self.notebook.add(self.log_frame, text="查看日志")
        self.notebook.add(self.status_frame, text="传感器状态")
        self.notebook.add(self.history_frame, text="历史数据")

        self.overview_tree = ttk.Treeview(self.overview_frame, columns=('Sensor ID', 'Sensor Name', 'Location', 'Value', 'Status', 'Timestamp'), show='headings')
        self.overview_tree.heading('Sensor ID', text='Sensor ID')
        self.overview_tree.heading('Sensor Name', text='Sensor Name')
        self.overview_tree.heading('Location', text='Location')
        self.overview_tree.heading('Value', text='Value')
        self.overview_tree.heading('Status', text='Status')
        self.overview_tree.heading('Timestamp', text='Timestamp')
        self.overview_tree.pack(fill=tk.BOTH, expand=True)

        self.sensor_tree = ttk.Treeview(self.sensor_frame, columns=('Sensor ID', 'Sensor Name', 'Location', 'Value', 'Status', 'Timestamp'), show='headings')
        self.sensor_tree.heading('Sensor ID', text='Sensor ID')
        self.sensor_tree.heading('Sensor Name', text='Sensor Name')
        self.sensor_tree.heading('Location', text='Location')
        self.sensor_tree.heading('Value', text='Value')
        self.sensor_tree.heading('Status', text='Status')
        self.sensor_tree.heading('Timestamp', text='Timestamp')
        self.sensor_tree.pack(fill=tk.BOTH, expand=True)

        self.log_tree = ttk.Treeview(self.log_frame, columns=('Timestamp', 'Log Level', 'Log Content'), show='headings')
        self.log_tree.heading('Timestamp', text='Timestamp')
        self.log_tree.heading('Log Level', text='Log Level')
        self.log_tree.heading('Log Content', text='Log Content')
        self.log_tree.pack(fill=tk.BOTH, expand=True)

        self.status_tree = ttk.Treeview(self.status_frame, columns=('Sensor ID', 'Sensor Name', 'Status', 'Timestamp'), show='headings')
        self.status_tree.heading('Sensor ID', text='Sensor ID')
        self.status_tree.heading('Sensor Name', text='Sensor Name')
        self.status_tree.heading('Status', text='Status')
        self.status_tree.heading('Timestamp', text='Timestamp')
        self.status_tree.pack(fill=tk.BOTH, expand=True)

        self.history_tree = ttk.Treeview(self.history_frame, columns=('Sensor ID', 'Sensor Name', 'Location', 'Value', 'Status', 'Timestamp'), show='headings')
        self.history_tree.heading('Sensor ID', text='Sensor ID')
        self.history_tree.heading('Sensor Name', text='Sensor Name')
        self.history_tree.heading('Location', text='Location')
        self.history_tree.heading('Value', text='Value')
        self.history_tree.heading('Status', text='Status')
        self.history_tree.heading('Timestamp', text='Timestamp')
        self.history_tree.pack(fill=tk.BOTH, expand=True)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "数据总览":
            self.set_view("overview")
        elif selected_tab == "查看数据":
            self.set_view("sensor")
        elif selected_tab == "查看日志":
            self.set_view("log")
        elif selected_tab == "传感器状态":
            self.set_view("status")
        elif selected_tab == "历史数据":
            self.set_view("history")

    def set_view(self, view):
        self.current_view = view
        if view == "overview":
            integrate_data(self.db, self.overview_tree)
        elif view == "sensor":
            sensor_data = self.db.get_latest_sensor_data()
            self.sensor_tree.delete(*self.sensor_tree.get_children())
            for data in sensor_data:
                sensor_id, sensor_name, value, location, status, sensor_type, timestamp = data
                unit = get_unit(sensor_type)
                self.sensor_tree.insert('', 'end', values=(sensor_id, sensor_name, location, f"{value}{unit}", status, timestamp))
        elif view == "log":
            system_logs = self.db.get_latest_system_logs()
            self.log_tree.delete(*self.log_tree.get_children())
            for log in system_logs:
                log_id, timestamp, log_level, log_content = log
                self.log_tree.insert('', 'end', values=(timestamp, log_level, log_content))
        elif view == "status":
            sensor_data = self.db.get_latest_sensor_data()
            self.status_tree.delete(*self.status_tree.get_children())
            for data in sensor_data:
                sensor_id, sensor_name, value, location, status, sensor_type, timestamp = data
                self.status_tree.insert('', 'end', values=(sensor_id, sensor_name, status, timestamp))
        elif view == "history":
            historical_data = self.db.get_historical_sensor_data()
            self.history_tree.delete(*self.history_tree.get_children())
            for data in historical_data:
                sensor_id, sensor_name, value, location, status, sensor_type, timestamp = data
                unit = get_unit(sensor_type)
                self.history_tree.insert('', 'end', values=(sensor_id, sensor_name, location, f"{value}{unit}", status, timestamp))

    def update_data(self):
        if self.current_view == "overview":  # 只有在数据总览界面时才更新数据
            sensor_data = self.gateway.collect_sensor_data()
            for sensor_name, data in sensor_data.items():
                sensor_id = self.gateway.sensors[sensor_name].sensor_id
                sensor_name = self.gateway.sensors[sensor_name].sensor_name
                self.db.insert_sensor_data(sensor_id, sensor_name, data['value'], data['location'], data['status'], data['type'])
                if data['status'] == 'WARNING':
                    self.db.insert_system_log('WARNING', f'{sensor_name} detected abnormal value: {data["value"]}')
                else:
                    self.db.insert_system_log('INFO', f'{sensor_name} data collected successfully.')

            weather_data = get_weather_from_internet(self.city)
            self.db.insert_weather_data(weather_data)
            self.db.insert_system_log('INFO', 'Weather data collected successfully.')

            # 更新显示的数据
            integrate_data(self.db, self.overview_tree)

        self.root.after(6000, self.update_data)  # 每6000ms

# 主程序
def main():
    gateway = Gateway()
    db = Database('smart_bridge.db')
    city = '嘉定'

    # 插入一些示例数据
    for _ in range(10):
        sensor_id = random.randint(1, 6)
        sensor_name = f"Sensor {sensor_id}"
        value = random.uniform(0, 500)
        location = "桥面"
        status = "normal"
        sensor_type = random.choice(['temperature', 'humidity', 'vibration', 'acceleration', 'deformation', 'stress'])
        db.insert_sensor_data(sensor_id, sensor_name, value, location, status, sensor_type)

    root = tk.Tk()
    app = App(root, gateway, db, city)
    root.mainloop()

if __name__ == '__main__':
    main()