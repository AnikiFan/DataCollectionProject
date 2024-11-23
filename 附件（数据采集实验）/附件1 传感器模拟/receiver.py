import socket
import struct


def parse_frame_payload(frame):
    frm_payload = frame[9:]
    payload_str = frm_payload.decode('utf-8')
    return payload_str


#def save_to_database(payload):
#自行设计sql功能

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 10000)
    sock.bind(server_address)

    print("Receiver is listening...")

    while True:
        data, address = sock.recvfrom(4096)
        print(f"Received frame from {address}: {data.hex()}")
        parsed_payload = parse_frame_payload(data)
        print(f"Parsed Payload: {parsed_payload}")
        #save_to_database(parsed_payload)

if __name__ == "__main__":
    main()