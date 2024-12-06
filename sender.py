import shutil
import struct
import random
import socket
from glob import glob
import logging
import time
import configparser
from random import gauss

import schedule
import sqlite3
import threading
import os
from utils import upload_log,run_continuously

class Sensor:
    def __init__(self, sensor_type, sensor_id,location):
        self.dev_addr = self.get_local_ip()
        self.fcnt = 0
        self.fport = 0x01
        self.sensor_type = sensor_type
        self.sensor_id = sensor_id
        self.location = location
        self.logger = self.setup_logger(sensor_id)
        self.status = self.generate_random_status()

    def get_local_ip(self):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return int(local_ip.replace('.', ''))

    def setup_logger(self, sensor_id):
        logger = logging.getLogger(f"Sensor_{sensor_id}")
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(os.path.join(os.curdir,'logs',f"sensor_{sensor_id}.log"))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def generate_frame(self):
        mhdr = 0x40
        fctrl = 0x80
        fopts = b''
        fport = self.fport
        sensor_data = self.generate_random_sensor_data(self.sensor_type)
        frm_payload = self.format_sensor_data(sensor_data)

        fhdr = struct.pack('>I', self.dev_addr) + struct.pack('B', fctrl) + struct.pack('>H', self.fcnt) + fopts
        frame = struct.pack('B', mhdr) + fhdr + struct.pack('B', fport) + frm_payload
        self.fcnt += 1
        self.log_sensor_status(sensor_data)
        if random.uniform(0, 1) > 0.9:
            self.status = self.generate_random_status()
        return frame

    def format_sensor_data(self, sensor_data):
        info = ' '+self.sensor_id
        if self.sensor_type == "Temperature":
            return f"T:{sensor_data['temperature']}{info}".encode('utf-8')
        elif self.sensor_type == "Pressure":
            return f"P:{sensor_data['pressure']}{info}".encode('utf-8')
        elif self.sensor_type == "Tilt":
            return f"TX:{sensor_data['tilt_x']},TY:{sensor_data['tilt_y']}{info}".encode('utf-8')
        elif self.sensor_type == "Humidity":
            return f"H:{sensor_data['humidity']}{info}".encode('utf-8')
        elif self.sensor_type == "Light":
            return f"L:{sensor_data['light']}{info}".encode('utf-8')
        elif self.sensor_type == "Vibration":
            return f"V:{sensor_data['vibration']}{info}".encode('utf-8')
        else:
            raise ValueError("Unsupported sensor type")

    @staticmethod
    def generate_random_sensor_data(sensor_type):
        if sensor_type == "Temperature":
            return {
                "temperature": round(random.uniform(25, 5), 2)
            }
        elif sensor_type == "Pressure":
            return {
                "pressure": max(round(random.gauss(200, 50), 2),0)
            }
        elif sensor_type == "Tilt":
            return {
                "tilt_x": round(random.gauss(0, 20), 2),
                "tilt_y": round(random.gauss(0, 20), 2)
            }
        elif sensor_type == "Humidity":
            return {
                "humidity": max(round(random.gauss(50, 10), 2),0)
            }
        elif sensor_type == "Light":
            return {
                "light": max(round(random.gauss(500, 200), 2),0)
            }
        elif sensor_type == "Vibration":
            return {
                "vibration": min(max(round(random.gauss(0.5, 0.1), 2),0),1)
            }
        else:
            raise ValueError("Unsupported sensor type")

    def generate_random_status(self):
        statuses = ["Normal", "Warning", "Fault"]
        return random.choices(statuses,weights=[94,5,1])[0]

    def log_sensor_status(self, sensor_data):
        status_message = f"Sensor ID: {self.sensor_id}, Sensor Type: {self.sensor_type}, Location: {self.location}, Status: {self.status}, Data: {sensor_data}"
        self.logger.info(status_message)

def work(sensor,sock,server_address):
    print('init')
    while True:
        frame = sensor.generate_frame()
        print(f"Generated Frame from {sensor.sensor_id}: {frame.hex()}")
        sock.sendto(frame, server_address)
        time.sleep(5)

def upload_logs():
    print('upload logs')
    for log in glob(os.path.join(os.curdir,'logs','*')):
        print('upload',log)
        upload_log(log)


def init_sensor():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.curdir,'configs','sensors.ini'))
    if os.path.exists(os.path.join(os.curdir,'logs')):
        shutil.rmtree(os.path.join(os.curdir,'logs'))
    os.mkdir(os.path.join(os.curdir,'logs'))
    sensors = []
    conn = sqlite3.connect(os.path.join(os.curdir,'identifier.sqlite'))
    cursor = conn.cursor()
    for section in config.sections():
        sensor_type = config[section]['type']
        sensor_id = config[section]['id']
        sensor_location = config[section]['location']
        sensors.append(Sensor(sensor_type, sensor_id,sensor_location))
        try:
            cursor.execute("INSERT INTO sensors (sensor_id,sensor_type,location) VALUES (?,?,?)",(sensor_id,sensor_type,sensor_location,))
            conn.commit()
        except sqlite3.IntegrityError:
            print(f"Sensor {sensor_id} already exists")
    conn.close()


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 10000)

    for sensor in sensors:
        # 设置为守护进程，使得主进程终止时子进程自动终止
        thread = threading.Thread(target=work,args=(sensor,sock,server_address),daemon=True)
        thread.start()
        print("active thread count:",threading.active_count())

    schedule.every(10).seconds.do(upload_logs)
    stop_run_continuously = run_continuously()
    time.sleep(60*60)
    stop_run_continuously.set()

if __name__ == '__main__':
    init_sensor()