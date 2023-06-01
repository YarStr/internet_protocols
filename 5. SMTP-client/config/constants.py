import json

with open('config/config.json', encoding='utf-8') as file:
    _config = json.load(file)

USER_NAME_FROM = _config['user_name_from']
USER_NAMES_TO = _config['user_names_to']
SUBJECT = _config['subject']
ATTACHMENTS = _config['attachments']

NICKNAME = _config['nickname']

BOUNDARY = _config['boundary']

HOST_ADDRESS = 'smtp.mail.ru'
PORT = 465
