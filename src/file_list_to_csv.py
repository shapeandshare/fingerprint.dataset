from typing import List
from pathlib import Path
from src.contracts.dtos.file_record import FileRecord
import json
import csv
from typing import List
from contracts.source_type import SourceType

# Load data set
data_set: List[FileRecord] = []
for child in (Path(".") / "hashes").glob("**/*.json"):
    if child.is_file():
        with open(child.resolve().as_posix(), mode="r", encoding="utf-8") as file:
            data_set.append(FileRecord(**json.load(file)))

# Convert to table format
tabular_representation: List = []

# Create headers
headers: List = ["hash.name", "path", "hash.data"]

tabular_representation.append(headers)
for record in data_set:
    name_hash = [hash for hash in record.hash if hash.source == SourceType.NAME][0]
    data_hash = [hash for hash in record.hash if hash.source == SourceType.DATA][0]
    row: List = [name_hash.value, record.path, data_hash.value]
    tabular_representation.append(row)

with open((Path(".") / "file_list.csv").resolve().as_posix(), mode="w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(tabular_representation)
