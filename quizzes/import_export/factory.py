from .csv_handler import CSVHandler
from .json_handler import JSONHandler


class ImportExportFactory:
    _handlers = {
        "json": JSONHandler(),
        "csv": CSVHandler(),
    }

    @classmethod
    def get_handler(cls, format_name):
        if format_name not in cls._handlers:
            raise ValueError(f"Неподдерживаемый формат: {format_name}")
        return cls._handlers[format_name]
