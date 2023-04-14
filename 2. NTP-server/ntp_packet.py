import struct


def get_fraction(number: float, byte_capacity: int):
    return int(number % float(1) * 2 ** (8 * byte_capacity))


class NTPPacket:
    PACK_FORMAT = '!2B 2b 4H 9I'

    def __init__(self, version_number=4):
        self.leap_indicator = 0
        self.version_number = version_number
        self.mode = 0
        self.stratum = 0
        self.poll = 0
        self.precision = 0
        self.root_delay = 0
        self.root_dispersion = 0
        self.reference_id = 0
        self.reference = 0
        self.originate = 0
        self.receive = 0
        self.transmit = 0

    def fill_client_fields(self, transmit_time: float):
        self.mode = 3
        self.transmit = transmit_time

    def fill_server_fields(self):
        self.mode = 4

    def get_packed_bytes(self) -> bytes:
        return struct.pack(
            self.PACK_FORMAT,

            (self.leap_indicator << 6) + (
                    self.version_number << 3) + self.mode,
            self.stratum,
            self.poll,
            self.precision,

            int(self.root_delay), get_fraction(self.root_delay, 2),
            int(self.root_dispersion), get_fraction(self.root_dispersion, 2),

            self.reference_id,

            int(self.reference),
            get_fraction(self.reference, 4),

            int(self.originate),
            get_fraction(self.originate, 4),

            int(self.receive),
            get_fraction(self.receive, 4),

            int(self.transmit),
            get_fraction(self.transmit, 4),
        )

    def fill_by_bytes(self, packet_in_bytes: bytes):
        packet_fields = struct.unpack(NTPPacket.PACK_FORMAT, packet_in_bytes)

        self.leap_indicator = packet_fields[0] >> 6
        self.version_number = packet_fields[0] >> 3 & 0b111
        self.mode = packet_fields[0] & 0b111

        self.stratum = packet_fields[1]
        self.poll = packet_fields[2]
        self.precision = packet_fields[3]

        self.root_delay = packet_fields[4] + packet_fields[5] / 2 ** 16
        self.root_dispersion = packet_fields[6] + packet_fields[7] / 2 ** 16

        self.reference_id = packet_fields[8]

        self.reference = packet_fields[9] + packet_fields[10] / 2 ** 32
        self.originate = packet_fields[11] + packet_fields[12] / 2 ** 32
        self.receive = packet_fields[13] + packet_fields[14] / 2 ** 32
        self.transmit = packet_fields[15] + packet_fields[16] / 2 ** 32

        return self
