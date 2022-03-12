""" Data Set Definition"""

import csv
import json
import logging
import shutil
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from tqdm import tqdm

from ...utils.hash import generate_file_path_hash, generate_hash
from ..missing_hashes_error import MissingHashesError
from ..source_type import SourceType
from .base_model import BaseModel
from .file_record import FileRecord


class DataSet(BaseModel):
    """
    DataSet DTO

    Attributes
    ----------
    search_path: Path
        The base path to form the data set from.
    name: str
        The name of the dataset.
    metadata_root: Optional[Path]
        The projects base.
    metadata_base: Optional[Path]
        The project base.
    hash_path: Optional[Path]
        The path to store hash data in.
    txt_file: Optional[Path]
        The index file path.
    csv_file: Optional[Path]
        The CSV report file path.
    pickle_file: Optional[Path]
        The pickled dataframe file path.
    """

    search_path: Path
    name: str

    metadata_root: Optional[Path]
    metadata_base: Optional[Path]
    hash_path: Optional[Path]
    txt_file: Optional[Path]
    csv_file: Optional[Path]
    pickle_file: Optional[Path]

    def __init__(self, recreate: bool = False, index: bool = True, metadata_root: Optional[str] = None, **data: Any):
        """
        Class Constructor

        Parameters
        ----------
        recreate: bool = False
            Recreate the dataset.
        index: bool = True
            Generate data set index during instantiation.
        data: Any
            Pydantic object definition for this DTO.
        """

        super().__init__(**data)

        if metadata_root:
            self.metadata_root = Path(metadata_root)
            self.metadata_root.mkdir(exist_ok=True, parents=True)
        else:
            self.metadata_root = Path(".")

        self.metadata_base = self.metadata_root / self.name
        if recreate and self.metadata_base.exists() and self.metadata_base.is_dir():
            logging.getLogger(__name__).warning(f"Remove pre-existing dataset ({self.name})")
            shutil.rmtree(self.metadata_base)
        self.metadata_base.mkdir(exist_ok=True, parents=True)

        self.hash_path = self.metadata_base / ".hashes"
        self.hash_path.mkdir(exist_ok=True, parents=True)

        self.txt_file = self.metadata_base / f"{self.name}.txt"
        self.csv_file = self.metadata_base / f"{self.name}.csv"
        self.pickle_file = self.metadata_base / f"{self.name}.df.pkl.bz2"

        if index:
            logging.getLogger(__name__).info("Auto-Indexing")
            self.build_index(recreate=recreate)

    def build_index(self, recreate: bool = False) -> None:
        """
        Build Data Set Index File

        Parameters
        ----------
        recreate: bool = False
            If False pre-existing index files will be used.
            If True index is rebuild regardless if its already exists.
        """

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
        """
        Perform Data Set Hashing

        Parameters
        ----------
        recreate: bool = False
            Recreate dataset hashes
        update: bool = False
            If False existing hashes won't be regenerated.
            If True all files in the dataset will be rehashed.
        """

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

                    file_record: FileRecord = generate_hash(
                        file_path=file_path, file_record=FileRecord.parse_file(file_record_path.resolve().as_posix())
                    )
                else:
                    file_record: FileRecord = generate_hash(file_path=file_path)

                with open(file_record_path.resolve().as_posix(), mode="w", encoding="utf-8") as file:
                    file.write(json.dumps(file_record.dict(exclude_unset=True), indent=4))

    def generate_csv(self) -> None:
        """Generate Report CSV"""

        logging.getLogger(__name__).info("Generating CSV")
        # Create headers
        headers: list = ["path", "hash", "size", "modified"]

        child_count: int = 0
        with open(self.csv_file.resolve().as_posix(), mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

            for child in tqdm(self.hash_path.glob("**/*.json")):
                if child.is_file():
                    child_count += 1
                    file_path: str = child.resolve().as_posix()
                    logging.getLogger(__name__).debug(child.stem)
                    record: FileRecord = FileRecord.parse_file(file_path)
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
            message: str = f"Unable to build CSV, no hash data found in {self.hash_path}"
            logging.getLogger(__name__).warning(message)
            raise MissingHashesError(message)

    def generate_dataframe(self) -> None:
        """Generate Report Dataframe"""

        logging.getLogger(__name__).info("Generating pickled dataframe")
        if not Path(self.csv_file.resolve().as_posix()).exists():
            self.generate_csv()
        files_df: pd.DataFrame = pd.read_csv(self.csv_file)
        files_df.to_pickle(path=self.pickle_file.resolve().as_posix(), compression={"method": "bz2"})
