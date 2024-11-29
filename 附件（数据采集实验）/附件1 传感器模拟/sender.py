import struct
import random
import socket
import logging
import time
import configparser
import threading

class Sensor:
    def __init__(self, sensor_type, sensor_id):
        self.dev_addr = self.get_local_ip()
        self.fcnt = 0
        self.fport = 0x01
        self.sensor_type = sensor_type
        self.sensor_id = sensor_id
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
        file_handler = logging.FileHandler(f"sensor_{sensor_id}.log")
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
        return frame

    def format_sensor_data(self, sensor_data):
        if self.sensor_type == "Temperature":
            return f"T:{sensor_data['temperature']}".encode('utf-8')
        elif self.sensor_type == "Pressure":
            return f"P:{sensor_data['pressure']}".encode('utf-8')
        elif self.sensor_type == "Tilt":
            return f"TX:{sensor_data['tilt_x']},TY:{sensor_data['tilt_y']}".encode('utf-8')
        elif self.sensor_type == "Humidity":
            return f"H:{sensor_data['humidity']}".encode('utf-8')
        elif self.sensor_type == "Light":
            return f"L:{sensor_data['light']}".encode('utf-8')
        elif self.sensor_type == "Vibration":
            return f"V:{sensor_data['vibration']}".encode('utf-8')
        else:
            raise ValueError("Unsupported sensor type")

    def generate_random_sensor_data(self, sensor_type):
        if sensor_type == "Temperature":
            return {
                "temperature": round(random.uniform(0, 50), 2)
            }
        elif sensor_type == "Pressure":
            return {
                "pressure": round(random.uniform(0, 1000), 2)
            }
        elif sensor_type == "Tilt":
            return {
                "tilt_x": round(random.uniform(-90, 90), 2),
                "tilt_y": round(random.uniform(-90, 90), 2)
            }
        elif sensor_type == "Humidity":
            return {
                "humidity": round(random.uniform(0, 100), 2)
            }
        elif sensor_type == "Light":
            return {
                "light": round(random.uniform(0, 1000), 2)
            }
        elif sensor_type == "Vibration":
            return {
                "vibration": round(random.uniform(0, 1), 2)
            }
        else:
            raise ValueError("Unsupported sensor type")

    def generate_random_status(self):
        statuses = ["Normal", "Warning", "Fault"]
        return random.choice(statuses)

    def log_sensor_status(self, sensor_data):
        status_message = f"Sensor ID: {self.sensor_id}, Sensor Type: {self.sensor_type}, Status: {self.status}, Data: {sensor_data}"
        self.logger.info(status_message)

def work(sensor,sock,server_address):
    print('init')
    while True:
        frame = sensor.generate_frame()
        print(f"Generated Frame from {sensor.sensor_id}: {frame.hex()}")
        sock.sendto(frame, server_address)
        time.sleep(5)

def main():
    config = configparser.ConfigParser()
    config.read('sensors.ini')

    sensors = []
    for section in config.sections():
        sensor_type = config[section]['type']
        sensor_id = config[section]['id']
        sensors.append(Sensor(sensor_type, sensor_id))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 10000)

    for sensor in sensors:
        thread = threading.Thread(target=work,args=(sensor,sock,server_address),daemon=True)
        thread.start()
        print("active thread count:",threading.active_count())
    
    while True:
        pass

if __name__ == "__main__":
    main()