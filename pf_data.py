import datetime

class PrefetchData:
    def __init__(self):
        self.file_name_offset = 0x10
        self.file_run_count_offset = 0xd0
        self.file_executed_time_offsets = [0x80, 0x88, 0x90, 0x98, 0xa0, 0xa8, 0xb0, 0xb8]
        self.volumes_offset = 0x30

        self.file_names = []
        self.file_executed_times = []

    def read_prefetch_file(self, file_path):
        self.file_names.clear()
        self.file_executed_times.clear()

        with open(file_path, 'rb') as file:
            file.seek(self.file_name_offset)
            file_name = file.read(60).decode('utf-16').split('\x00')[0]

            file.seek(self.file_run_count_offset)
            file_run_count = int.from_bytes(file.read(4), byteorder='little')

            for offset in self.file_executed_time_offsets:
                file.seek(offset)
                file_executed_time = int.from_bytes(file.read(8), byteorder='little')
                converted_real_time = file_executed_time / 10_000_000 - 11_644_473_600
                self.file_executed_times.append(converted_real_time)

            self.file_names.append(file_name)

            datetime_objects = []
            for timestamp in self.file_executed_times:
                try:
                    dt_object = datetime.datetime.fromtimestamp(timestamp)
                    datetime_objects.append(dt_object)
                except OSError as e:
                    print(f"Invalid timestamp: {timestamp}: {e}")

            file.seek(self.volumes_offset)
            file_content_byte = file.read().replace(b"\x00", b"")

            volumes = []
            start_index = 0

            while True:
                start_index = file_content_byte.find(b"\\VOLUME", start_index)
                if start_index == -1:
                    break
                end_index = file_content_byte.find(b"\\VOLUME", start_index + 1)
                if end_index == -1:
                    end_index = len(file_content_byte)
                volume_info = file_content_byte[start_index:end_index]
                volumes.append(volume_info)
                start_index = end_index

            return self.file_names, file_run_count, datetime_objects, volumes