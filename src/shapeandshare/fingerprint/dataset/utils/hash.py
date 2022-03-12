""" Hash Functions """

import hashlib
from pathlib import Path
from typing import Optional

from ..contracts.dtos.file_record import FileRecord
from ..contracts.source_type import SourceType


def generate_file_path_hash(file_path: str) -> str:
    """
    Generate File Path Hash

    Parameters
    ----------
    file_path: str

    Returns
    -------
    hex_digest: str
    """

    filename_hash = hashlib.sha256(file_path.encode())
    return filename_hash.hexdigest()


def generate_hash(file_path: str, file_record: Optional[FileRecord] = None) -> FileRecord:
    """
    Generate File Hash

    Parameters
    ----------
    file_path: str
    file_record: Optional[FileRecord] = None

    Returns
    -------
    file_record: FileRecord
    """

    if file_record:
        partial_record: dict = file_record.dict(exclude_unset=True)
    else:
        partial_record: dict = {}

    if "path" not in partial_record:
        partial_record["path"] = file_path

    if "id" in partial_record:
        del partial_record["id"]

    if "hash" not in partial_record:
        partial_record["hash"] = []

    if "size" not in partial_record:
        partial_record["size"] = (
            Path(file_path).stat().st_size
        )  # Size in bytes | https://docs.python.org/3/library/os.html#os.stat_result

    if "modified" not in partial_record:
        partial_record["modified"] = Path(file_path).stat().st_mtime  # unix time stamp

    data: list = [hash for hash in partial_record["hash"] if hash["source"] == SourceType.DATA]
    partial_record["hash"] = data  # filter out other types ..

    if len(data) < 1:
        with open(file_path, mode="rb") as file:
            file_hash = hashlib.sha256(file.read())
            file_hex_digest: str = file_hash.hexdigest()
            partial_record["hash"].append({"source": SourceType.DATA, "type": "sha256", "value": file_hex_digest})

    return FileRecord(**partial_record)
