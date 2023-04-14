from datetime import datetime, date
from time import time
import socket

from ntp_packet import NTPPacket

FORMAT_DIFFERENCE = (date(1970, 1, 1)
                     - date(1900, 1, 1)).days * 24 * 3600

HOST = '127.0.0.1'
PORT = 123
TIMEOUT = 5


def get_current_time() -> float:
    return time() + FORMAT_DIFFERENCE


def main():
    packet = NTPPacket()
    packet.fill_client_fields(get_current_time())

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)
    client_socket.sendto(packet.get_packed_bytes(), (HOST, PORT))

    try:
        packet_in_bytes, address = client_socket.recvfrom(48)
        arrive_time = get_current_time()

        answer = NTPPacket()
        answer.fill_by_bytes(packet_in_bytes)

        time_difference = (answer.receive - answer.originate
                           - arrive_time + answer.transmit)
        server_time = datetime.fromtimestamp(time() + time_difference)

        result = f'Current time is {server_time}'
        print(result)

    except socket.timeout:
        print('Request time out')


if __name__ == '__main__':
    main()
