import csv
import json
import logging
import shutil
from pathlib import Path
from typing import Any, List, Optional

import pandas as pd
from tqdm import tqdm

from ...utils.hash import generate_file_path_hash, generate_hash
from ..missing_hashes_error import MissingHashesError
from ..source_type import SourceType
from .base_model import BaseModel
from .file_record import FileRecord


class DataSet(BaseModel):
    search_path: Path
    name: str

    metadata_base: Optional[Path]
    hash_path: Optional[Path]
    txt_file: Optional[Path]
    csv_file: Optional[Path]
    pickle_file: Optional[Path]

    def __init__(self, recreate: bool = False, index: bool = True, **data: Any):
        super().__init__(**data)

        self.metadata_base = Path(".") / self.name
        self.hash_path = self.metadata_base / ".hashes"
        self.txt_file = self.metadata_base / f"{self.name}.txt"
        self.csv_file = self.metadata_base / f"{self.name}.csv"
        self.pickle_file = self.metadata_base / f"{self.name}.df.pkl.bz2"

        if recreate and self.metadata_base.exists() and self.metadata_base.is_dir():
            shutil.rmtree(self.metadata_base)
        self.metadata_base.mkdir(exist_ok=True, parents=True)
        self.hash_path.mkdir(exist_ok=True, parents=True)

        if index:
            self.build_index()

    def build_index(self, recreate: bool = False) -> None:
        logging.getLogger(__name__).info("Indexing Search Path")
        if recreate and self.txt_file.exists():
            logging.getLogger(__name__).info("Removing existing index")
            self.txt_file.unlink()

        if self.txt_file.exists():
            logging.getLogger(__name__).info("Index already exists, skipping")
        else:
            with open(file=self.txt_file.resolve().as_posix(), mode="w", encoding="utf-8") as file:
                for child in tqdm(self.search_path.glob("**/*")):
                    if child.is_file():
                        file_path: str = child.as_posix()
                        file.write(f"{file_path}\r\n")
                        logging.getLogger(__name__).debug(file_path)

    def hash(self, recreate: bool = False, update: bool = False) -> None:
        logging.getLogger(__name__).info("Hashing Files")

        if recreate and self.hash_path.exists():
            logging.getLogger(__name__).info("Removing existing hashes")
            shutil.rmtree(self.hash_path)
            self.hash_path.mkdir(exist_ok=True, parents=True)

        if not self.txt_file.exists():
            self.build_index(recreate=recreate)

        with open(file=self.txt_file.resolve().as_posix(), mode="r", encoding="utf-8") as file:
            for line in tqdm(file):
                file_path: str = line.rstrip()
                logging.getLogger(__name__).debug(file_path)

                file_path_hash: str = generate_file_path_hash(file_path=file_path)
                file_record_path: Path = self.hash_path / f"{file_path_hash}.json"
                if file_record_path.exists():
                    if not update:
                        continue

                    with open(file_record_path.resolve().as_posix(), mode="r", encoding="utf-8") as file:
                        file_record: FileRecord = generate_hash(
                            file_path=file_path, file_record=FileRecord(**json.load(file))
                        )
                else:
                    file_record: FileRecord = generate_hash(file_path=file_path)

                with open(file_record_path.resolve().as_posix(), mode="w", encoding="utf-8") as file:
                    file.write(json.dumps(file_record.dict(exclude_unset=True), indent=4))

    def generate_csv(self) -> None:
        logging.getLogger(__name__).info("Generating CSV")
        # Create headers
        headers: List = ["path", "hash", "size", "modified"]

        child_count: int = 0
        with open(self.csv_file.resolve().as_posix(), mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

            for child in tqdm(self.hash_path.glob("**/*.json")):
                if child.is_file():
                    child_count += 1
                    file_path: str = child.resolve().as_posix()
                    logging.getLogger(__name__).debug(child.stem)
                    with open(file=file_path, mode="r", encoding="utf-8") as file:
                        record: FileRecord = FileRecord(**json.load(file))
                        data_hash = [hash for hash in record.hash if hash.source == SourceType.DATA][0]
                        writer.writerow(
                            [
                                record.path,
                                data_hash.value,
                                record.size,
                                record.modified,
                            ]
                        )
        if child_count == 0:
            self.csv_file.unlink(missing_ok=True)
            logging.getLogger(__name__).warning(f"Unable to build CSV, no hash data found in {self.hash_path}")
            raise MissingHashesError(f"Unable to build CSV, no hash data found in {self.hash_path}")

    def generate_dataframe(self) -> None:
        logging.getLogger(__name__).info("Generating pickled dataframe")
        if not Path(self.csv_file.resolve().as_posix()).exists():
            self.generate_csv()
        files_df: pd.DataFrame = pd.read_csv(self.csv_file)
        files_df.to_pickle(path=self.pickle_file.resolve().as_posix(), compression={"method": "bz2"})
