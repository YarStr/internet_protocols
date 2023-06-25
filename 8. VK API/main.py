import socket
import ssl
import json

HOST = 'api.vk.com'
PORT = 443


def print_friend_list() -> None:
    with open('config.txt', 'r') as file:
        token = file.readline()

    user_vk_id = input('Введите токен пользователя: ')

    for friend in get_friends_of_user(token, user_vk_id):
        print(friend)


def get_friends_of_user(token: str, user_id: str) -> list:
    ssl_contex = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_contex.check_hostname = False
    ssl_contex.verify_mode = ssl.CERT_NONE

    with socket.create_connection((HOST, PORT)) as sock:
        with ssl_contex.wrap_socket(
                sock, server_hostname=HOST) as client_socket:
            body = get_message_body(token, user_id)
            message = get_prepared_message(body)

            answer = send_request(client_socket, message).split('\r\n\r\n')[-1]
            parsed_answer = json.loads(answer)

            return [f'{user["first_name"]} {user["last_name"]}' for user in
                    parsed_answer['response']['items']]


def get_message_body(token: str, user_id: str) -> dict:
    return {
        'method': 'GET',
        'url': '/method/friends.get',
        'params': {
            'access_token': token,
            'user_id': user_id,
            'fields': 'nickname',
            'v': '5.131',
        },
        'version': '1.1',
        'headers': {'host': HOST},
        'body': None
    }


def get_prepared_message(data: dict) -> str:
    message = data['method'] + ' ' + data['url'] + '?'

    parameters = '&'.join(
        (f'{arg}={value}' for arg, value in data['params'].items()))
    message += parameters

    message += ' ' + 'HTTP/' + data['version'] + '\n'
    for header, value in data['headers'].items():
        message += f'{header}: {value}\n'
    message += '\n'

    return message


def send_request(sock: socket.socket, message: str) -> str:
    sock.send(message.encode())
    sock.settimeout(1)
    recv_data = sock.recv(65535)

    while True:
        try:
            buf = sock.recv(65535)
            recv_data += buf
        except socket.timeout:
            break

    return recv_data.decode()


if __name__ == '__main__':
    print_friend_list()
