import datetime
import socket
import time
import configparser

from ntp_packet import NTPPacket

config = configparser.ConfigParser()
config.read('configuration.ini')

DELAY = int(config['DEFAULT']['delay'])
FORMAT_DIFFERENCE = (datetime.date(1970, 1, 1)
                     - datetime.date(1900, 1, 1)).days * 24 * 3600

HOST = '127.0.0.1'
PORT = 123


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))

    while True:
        packet_in_bytes, address = server_socket.recvfrom(48)

        answer = NTPPacket()
        answer.fill_by_bytes(packet_in_bytes)
        answer.fill_server_fields()

        answer.originate = answer.transmit
        answer.receive = time.time() + FORMAT_DIFFERENCE + DELAY
        answer.transmit = time.time() + FORMAT_DIFFERENCE

        server_socket.sendto(answer.get_packed_bytes(), address)


if __name__ == '__main__':
    main()
