import socket
from argparse import ArgumentParser, Namespace

MIN_PORT = 1
MAX_PORT = 2 ** 16 - 1
MESSAGE = b'\x13' + b'\x00' * 39 + b'\x6f\x89\xe9\x1a\xb6\xd5\x3b\xd3'


def scan_port(host: str, port: int) -> None:
    scan_tcp_port(host, port)
    scan_udp_port(host, port)


def scan_tcp_port(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        try:
            sock.connect((host, port))
            print_opened_port('TCP', port)
        except (socket.error, socket.timeout, TimeoutError, OSError):
            return


def scan_udp_port(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(3)
        try:
            sock.sendto(MESSAGE, (host, port))
            data, _ = sock.recvfrom(1024)
            print_opened_port('UDP', port)
        except socket.error:
            pass


def print_opened_port(protocol: str, port: int) -> None:
    print(f'{protocol} {port} is open')


def get_argument_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_help = True
    parser.add_argument("host", type=str, help="host")
    parser.add_argument("start_port", type=int, help="start of scanning ports")
    parser.add_argument("end_port", type=int, help="end of scanning ports")
    return parser


def validate_arguments(arguments: Namespace) -> None:
    start_port = arguments.start_port
    end_port = arguments.end_port

    if start_port >= end_port:
        raise Exception('Start port must be less then End port')

    if ((MIN_PORT <= start_port <= MAX_PORT)
            and (MIN_PORT <= end_port <= MAX_PORT)):
        return
    else:
        raise Exception(f'Value of port must be from {MIN_PORT} to {MAX_PORT}')


if __name__ == '__main__':
    args = get_argument_parser().parse_args()
    validate_arguments(args)
    for port in range(args.start_port, args.end_port + 1):
        scan_port(args.host, port)
