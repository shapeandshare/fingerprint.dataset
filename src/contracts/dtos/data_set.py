import csv
import json
import logging
from pathlib import Path
from typing import Any, List, Optional

import pandas as pd
from pydantic import BaseModel
from tqdm import tqdm

from .file_record import FileRecord
from ..source_type import SourceType
from ...utils.hash import generate_file_path_hash, generate_hash


class DataSet(BaseModel):
    search_path: Path
    name: str

    metadata_base: Optional[Path]
    hash_path: Optional[Path]

    txt_file: Optional[str]
    csv_file: Optional[str]
    pickle_file: Optional[str]

    def __init__(self, **data: Any):
        super().__init__(**data)

        self.metadata_base = Path(".") / self.name
        self.hash_path = self.metadata_base / "hashes"

        self.txt_file = (self.metadata_base / f"{self.name}.txt").resolve().as_posix()
        self.csv_file = (self.metadata_base / f"{self.name}.csv").resolve().as_posix()
        self.pickle_file = (self.metadata_base / f"{self.name}.df.pkl.bz2").resolve().as_posix()

        self.hash_path.mkdir(exist_ok=True, parents=True)

    def generate_file_list(self) -> None:
        logging.info("Reviewing directory structure")
        with open(file=self.txt_file, mode="w", encoding="utf-8") as file:
            for child in tqdm(self.search_path.glob("**/*")):
                if child.is_file():
                    file.write(f"{child.resolve().as_posix()}\r\n")

    def generate_file_list_hashes(self) -> None:
        logging.info("Generating file hashes")
        with open(file=self.txt_file, mode="r", encoding="utf-8") as file:
            for line in tqdm(file):
                file_path: str = line.rstrip()
                file_path_hash: str = generate_file_path_hash(file_path=file_path)
                file_record_path: Path = self.hash_path / f"{file_path_hash}.json"

                if file_record_path.exists():
                    with open(file_record_path.resolve().as_posix(), mode="r", encoding="utf-8") as file:
                        file_record: FileRecord = generate_hash(
                            file_path=file_path, file_record=FileRecord(**json.load(file))
                        )
                else:
                    file_record: FileRecord = generate_hash(file_path=file_path)

                with open(file_record_path.resolve().as_posix(), mode="w", encoding="utf-8") as file:
                    file.write(json.dumps(file_record.dict(exclude_unset=True), indent=4))

    def build_csv(self):
        logging.info("Generating csv")
        # Create headers
        headers: List = ["path", "hash.data", "size", "modified"]

        with open(self.csv_file, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

            for child in tqdm(self.hash_path.glob("**/*.json")):
                if child.is_file():
                    with open(file=child.resolve().as_posix(), mode="r", encoding="utf-8") as file:
                        record: FileRecord = FileRecord(**json.load(file))
                        data_hash = [hash for hash in record.hash if hash.source == SourceType.DATA][0]
                        writer.writerow([child.resolve().as_posix(), data_hash.value, record.size, record.modified])

    def export_to_df(self):
        logging.info("Generating pickled dataframe")
        files_df: pd.DataFrame = pd.read_csv(self.csv_file)
        files_df.to_pickle(path=self.pickle_file, compression={"method": "bz2"})
