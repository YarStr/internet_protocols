# Сервер точного времени

Задание выполнил Страхов Ярослав, студент группы КН-201.

## Описание

Реализация SNTP-сервера, отправляющего время с задержкой на указанное
число секунд. Задержка может быть как положительной, так и отрицательной.

## Описание модулей 

Основная логика работы представлена в файле _sntp_server.py_.
Файл _sntp_client.py_ представляет реализацию тестового клиента
для отправки и получения NTP-пакетов от сервера.

В папке _resources_ находится конфигурационный файл _configuration.ini_
и _ntp_packet.py_, хранящий класс для представления NTP-пакета.

## Использование

- Запуск сервера: ``python sntp_server.py``
- Запуск тестового клиента: ``python sntp_client.py``

