import base64
import datetime
import mimetypes
import re
import socket
import ssl
from os import listdir
from os.path import isfile, join

from config.constants import *

with open('config/password.txt', 'r', encoding='UTF-8') as password_file:
    PASSWORD = password_file.read().strip()


class SMTPException(Exception):
    pass


def send_letter_with_ssl() -> None:
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    with socket.create_connection((HOST_ADDRESS, PORT)) as sock:
        send_letter(sock, ssl_context)


def send_letter(sock: socket.socket, context: ssl.SSLContext) -> None:
    try:
        with context.wrap_socket(sock, server_hostname=HOST_ADDRESS) as client:
            print(client.recv(65536))
            print(handle_request(client, f'ehlo {socket.gethostname()}'))

            login_base_64 = base64.b64encode(USER_NAME_FROM.encode()).decode()
            password_base_64 = base64.b64encode(PASSWORD.encode()).decode()

            print(handle_request(client, 'AUTH LOGIN'))
            print(handle_request(client, login_base_64))
            print(handle_request(client, password_base_64))

            print(handle_request(client, f'MAIL FROM:{USER_NAME_FROM}'))

            for user_name in USER_NAMES_TO:
                print(handle_request(client, f'RCPT TO:{user_name}'))

            print(handle_request(client, 'DATA'))

            print(handle_request(client, get_prepared_message()))

    except SMTPException as exception:
        print_exception_message(exception)


def handle_request(sock: socket.socket, request_message: str) -> str:
    sock.send((request_message + '\n').encode())
    recv_data = sock.recv(65535).decode()
    check_reply_code(recv_data)
    return recv_data


def get_prepared_message() -> str:
    headers = get_headers()
    message_body = get_message_body()
    message = f'{headers}\n{message_body}\n.\n'
    return message


def print_exception_message(exception: SMTPException):
    print(f'Ошибка! Вернулся SMTP-ответ с кодом {exception.args[0]}:\n'
          f'{exception.args[1]}')


def check_reply_code(recv_data: str) -> None:
    if recv_data[0] in '45':
        raise SMTPException(recv_data[0:3], recv_data[4:])


def get_headers():
    date = get_date()
    user_names_to_list = ', '.join(USER_NAMES_TO)
    return f'from: {NICKNAME} <{USER_NAME_FROM}>\n' \
           f'to: {user_names_to_list}\n' \
           f'date: {date}\n' \
           f'subject:{SUBJECT}\n' \
           f'MIME-Version: 1.0\n' \
           f'Content-Type: multipart/mixed;\n\tboundary={BOUNDARY}\n'


def get_message_body():
    content = get_content()
    attachments = get_attachments()
    return f'--{BOUNDARY}\n' \
           f'Content-Type: text/html; charset=utf-8\n' \
           f'\n' \
           f'{content}\n' \
           f'--{BOUNDARY}\n' \
           f'{attachments}\n' \
           f'--{BOUNDARY}--'


def get_date() -> str:
    date = datetime.datetime.utcnow()
    formatted_date = date.strftime('%a, %d %B %Y %H:%M:%S')
    return f'{formatted_date} PST'


def get_content() -> str:
    with open('message.txt', encoding='utf-8') as message:
        return get_text_with_stuffing_points(message.read())


def get_attachments() -> str:
    attachments = f''
    attachments_list = get_attachments_list()

    for attachment_name in attachments_list:
        content_type = get_content_type(attachment_name)
        attachment = read_attachment_from_file(
            f'{ATTACHMENTS}/{attachment_name}')

        attachments += f'Content-Disposition: attachment;\n' \
                       f'\tfilename="{attachment_name}"\n' \
                       f'Content-Transfer-Encoding: base64\n' \
                       f'Content-Type: {content_type};\n' \
                       f'\tname="{attachment_name}"\n' \
                       f'\n' \
                       f'{attachment}\n' \
                       f'--{BOUNDARY}\n'

    return attachments


def get_text_with_stuffing_points(text: str):
    regex = re.compile(r'\n(?=(\.+\n))')
    return regex.sub(lambda _: '\n.', text)


def get_attachments_list():
    return [f for f in listdir(ATTACHMENTS) if isfile(join(ATTACHMENTS, f))]


def get_content_type(attachment: str) -> str:
    return mimetypes.guess_type(attachment)[0]


def read_attachment_from_file(file_name: str) -> str:
    with open(file_name, 'rb') as attachment_file:
        attachment = attachment_file.read()
        return base64.b64encode(attachment).decode()


if __name__ == '__main__':
    send_letter_with_ssl()
