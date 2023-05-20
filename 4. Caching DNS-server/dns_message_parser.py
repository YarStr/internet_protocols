import struct
from enum import Enum, unique


@unique
class Type(Enum):
    A = 1
    NS = 2


class DNSMessageParser:
    def __init__(self, data):
        self._data = data
        self._header = self._parse_header()

        int_flags = bin(self._header[1])
        self._flags = '0' * (16 - len(int_flags) + 2) + str(int_flags)[2:]

        self._is_answer = self._flags[0]

        self.name, self.q_type, position = self._parse_question()

        self._question_len = position
        self.info = self._parse_body(position) if self._is_answer else None

    def _parse_header(self) -> tuple:
        header = struct.unpack('!6H', self._data[0:12])
        return header

    def _parse_question(self) -> tuple:
        name, end = self._parse_name(12)
        qr_type, qr_class = struct.unpack('!HH', self._data[end: end + 4])
        return name, qr_type, end + 4

    def _parse_body(self, start: int) -> list:
        answer_list, answer_end = self._parse_record(start, 3)
        authority_list, authority_end = self._parse_record(answer_end, 4)
        additional_list, additional_end = self._parse_record(authority_end, 5)

        if len(answer_list) != 0:
            for answer in answer_list:
                self._print_record(answer[0], answer[1], answer[3])

        if len(authority_list) != 0:
            for authority in authority_list:
                self._print_record(authority[0], authority[1], authority[3])

        if len(additional_list) != 0:
            for additional in additional_list:
                self._print_record(additional[0], additional[1], additional[3])

        return answer_list + authority_list + additional_list

    def _parse_name(self, start: int) -> tuple[str, int]:
        name_list = []
        position = start
        end = start
        flag = False

        while True:
            if self._data[position] > 63:
                if not flag:
                    end = position + 2
                    flag = True
                position = (((self._data[position] - 192) << 8)
                            + self._data[position + 1])
                continue

            else:
                length = self._data[position]
                if length == 0:
                    if not flag:
                        end = position + 1
                    break
                position += 1
                name_list.append(self._data[position: position + length])
                position += length

        name = '.'.join([i.decode('ascii') for i in name_list])
        return name, end

    def _parse_record(self, start: int, number: int) -> tuple[list, int]:
        offset = start
        record_list = []

        for i in range(self._header[number]):
            name, end = self._parse_name(offset)
            offset = end

            record_type, record_class, ttl, length = (
                struct.unpack('!2HIH', self._data[offset: offset + 10]))
            offset += 10

            if record_type == 1:
                ip = struct.unpack('!4B', self._data[offset: offset + 4])
                offset += 4
                record_list.append((name, record_type, ttl, ip))

            elif record_type == 2:
                dns_server_name, dns_name_end = self._parse_name(offset)
                offset = dns_name_end
                record_list.append((name, record_type, ttl, dns_server_name))

            else:
                offset += length

        return record_list, offset

    @staticmethod
    def _print_record(name, record_type, value):
        information = f'{name=}, {record_type=}, {value=}'
        print(information)

    def make_answer_in_bytes(self, non_bytes_answer: tuple) -> bytes:
        header = list(self._header[:12])
        header[1] = 2 ** 15
        header[3] = len(non_bytes_answer)

        question = self._data[12: self._question_len]

        domain_name_position = b'\xc0\x0c'

        answers = b''

        if self.q_type == Type.A.value:
            for record in non_bytes_answer:
                address = record[0]
                ttl = record[2]
                item = struct.pack('!4B', *address)
                answers += (
                        domain_name_position
                        + struct.pack('!HHIH', self.q_type, 1, ttl, 4)
                        + item
                )

        elif self.q_type == Type.NS.value:
            for record in non_bytes_answer:
                address = record[0]
                ttl = record[2]

                octets = address.split('.')
                result = []

                for octet in octets:
                    result.append(len(octet))
                    for b in octet:
                        result.append(ord(b))
                result.append(0)

                item = struct.pack(f'!{len(result)}B', *result)
                length = len(item)

                answers += (
                        domain_name_position
                        + struct.pack('!HHIH', self.q_type, 1, ttl, length)
                        + item
                )

        else:
            raise Exception('Unsupported request type!')

        answer = struct.pack('!6H', *header) + question + answers
        return answer
