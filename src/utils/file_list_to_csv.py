import csv
import json
from pathlib import Path
from typing import List

from tqdm import tqdm

from ..contracts.dtos.file_record import FileRecord
from ..contracts.source_type import SourceType


def build_csv():
    # Create headers
    headers: List = ["path", "hash.data", "size", "modified"]

    print("Building CSV")
    with open((Path(".") / "file_list.csv").resolve().as_posix(), mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)

        for child in tqdm((Path(".") / "hashes").glob("**/*.json")):
            if child.is_file():
                with open(child.resolve().as_posix(), mode="r", encoding="utf-8") as file:
                    record: FileRecord = FileRecord(**json.load(file))
                    data_hash = [hash for hash in record.hash if hash.source == SourceType.DATA][0]
                    writer.writerow([child.resolve().as_posix(), data_hash.value, record.size, record.modified])


if __name__ == "__main__":
    build_csv()
