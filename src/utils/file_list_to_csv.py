import csv
import json
from pathlib import Path
from typing import List

from tqdm import tqdm

from ..contracts.dtos.file_record import FileRecord
from ..contracts.source_type import SourceType

# Create headers
headers: List = ["hash.name", "path", "hash.data"]

print("Building CSV")
with open((Path(".") / "file_list.csv").resolve().as_posix(), mode="w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(headers)

    for child in tqdm((Path(".") / "hashes").glob("**/*.json")):
        if child.is_file():
            with open(child.resolve().as_posix(), mode="r", encoding="utf-8") as file:
                record: FileRecord = FileRecord(**json.load(file))
                name_hash = [hash for hash in record.hash if hash.source == SourceType.NAME][0]
                data_hash = [hash for hash in record.hash if hash.source == SourceType.DATA][0]
                writer.writerow([name_hash.value, record.path, data_hash.value])
