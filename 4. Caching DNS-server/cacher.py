import pickle
import time
from typing import Any, Optional


class Cacher:
    def __init__(self, cache_file_name: str = 'cache'):
        self._cache_file_name = cache_file_name
        self._check_is_cache_exists()
        self._data = self._load()

    def add_record(self, name, record_type, ttl, value) -> None:
        record = (value, time.time(), ttl)
        key = (name, record_type)

        if key in self._data:
            self._data[key].append(record)
        else:
            self._data[key] = [record]

    def get_record(self, key) -> Optional[Any]:
        result_records = []

        if key in self._data:
            records = self._data[key]

            for record in records:
                creation_time = record[1]
                ttl = record[2]

                if creation_time + ttl > time.time():
                    result_records.append(record)

        return result_records

    def cache(self) -> None:
        with open(self._cache_file_name, 'wb') as file:
            pickle.dump(self._data, file)

    def _load(self) -> dict:
        try:
            with open(self._cache_file_name, 'rb') as file:
                data = self._delete_old_records(pickle.load(file))
            print('Кэш загружен')
            return data

        except EOFError:
            print('Кэш пуст')
            return dict()

    @staticmethod
    def _delete_old_records(cached_records: dict) -> dict:
        result = dict()
        for key, records in cached_records.items():
            result[key] = []
            for record in records:
                creation_time = record[1]
                ttl = record[2]
                if creation_time + ttl > time.time():
                    result[key].append(record)

        return result

    def _check_is_cache_exists(self):
        try:
            with open(self._cache_file_name, 'rb'):
                pass

        except FileNotFoundError:
            with open(self._cache_file_name, 'wb'):
                pass
