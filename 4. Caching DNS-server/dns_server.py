from socket import socket, AF_INET, SOCK_DGRAM, timeout
from typing import Optional

from cacher import Cacher
from dns_message_parser import DNSMessageParser

DNS_PORT = 53
HTTP_PORT = 80
GOOGLE_DNS_SERVER_IP = '8.8.8.8'
REQUEST_SIZE = 2048


class DNSServer:
    def __init__(self, cache: Cacher, dns_ip: str = GOOGLE_DNS_SERVER_IP):
        self._cache = cache
        self._dns_ip = dns_ip
        self._host_ip = get_host_ip()

        self._dns_sock = socket(AF_INET, SOCK_DGRAM)
        self._dns_sock.bind((self._host_ip, DNS_PORT))

    def start(self) -> None:
        while True:
            self._handle_request()
            self._cache.cache()

    def _handle_request(self) -> None:
        while True:
            try:
                data, client_address = self._dns_sock.recvfrom(REQUEST_SIZE)
            except timeout:
                continue
            else:
                request = DNSMessageParser(data)
                answer = self._get_answer_from_cache(request)
                if answer is None:
                    answer = self._get_answer(data)
                    self._add_data_in_cache(answer)
                self._dns_sock.sendto(answer, client_address)
                break

    def _get_answer(self, data: bytes) -> bytes:
        with socket(AF_INET, SOCK_DGRAM) as sock:
            sock.sendto(data, (self._dns_ip, DNS_PORT))
            answer = sock.recvfrom(REQUEST_SIZE)[0]
        return answer

    def _get_answer_from_cache(
            self, request: DNSMessageParser) -> Optional[bytes]:

        answer_from_cache = self._cache.get_record(
            (request.name, request.q_type))

        if not answer_from_cache:
            return None

        return request.make_answer_in_bytes(answer_from_cache)

    def _add_data_in_cache(self, data: bytes) -> None:
        parsed_answer = DNSMessageParser(data)
        for info in parsed_answer.info:
            self._cache.add_record(*info)


def get_host_ip() -> str:
    with socket(AF_INET, SOCK_DGRAM) as sock:
        sock.connect((GOOGLE_DNS_SERVER_IP, HTTP_PORT))
        return sock.getsockname()[0]


if __name__ == '__main__':
    DNSServer(Cacher()).start()
