import socket
import os
import sqlite3
def parse_frame_payload(frame):
    frm_payload = frame[9:]
    payload_str = frm_payload.decode('utf-8')
    return payload_str


def init_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 10000)
    sock.bind(server_address)

    print("Receiver is listening...")

    while True:
        data, address = sock.recvfrom(4096)
        print(f"Received frame from {address}: {data.hex()}")
        parsed_payload = parse_frame_payload(data)
        data = parsed_payload.split(' ')[-2]
        sensor_id = parsed_payload.split(' ')[-1]
        conn = sqlite3.connect(os.path.join(os.curdir,'identifier.sqlite'))
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO sensor_data (sensor_id,  data) VALUES (?,?)",(sensor_id,data))
            conn.commit()
        except :
            print("Failed to insert data")
        conn.close()

if __name__ == '__main__':
    init_receiver()