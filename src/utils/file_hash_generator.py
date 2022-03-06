import hashlib
import json
from pathlib import Path
from typing import List, Optional, Dict

from tqdm import tqdm

from ..contracts.dtos.file_record import FileRecord
from ..contracts.source_type import SourceType


def serialize_file_data(files: List[FileRecord]) -> List:
    raw_list: List = []
    for file_obj in files:
        raw_list.append(file_obj.dict(exclude_unset=True))
    return raw_list


def generate_file_path_hash(file_path: str) -> str:
    filename_hash = hashlib.sha256(file_path.encode())
    return filename_hash.hexdigest()


def generate_hash(file_path: str, file_record: Optional[FileRecord] = None) -> FileRecord:
    if file_record:
        partial_record: Dict = file_record.dict(exclude_unset=True)
    else:
        partial_record: Dict = {}

    if "path" not in partial_record:
        partial_record["path"] = file_path

    if "id" in partial_record:
        del partial_record["id"]

    if "hash" not in partial_record:
        partial_record["hash"] = []

    if "size" not in partial_record:
        partial_record["size"] = Path(file_path).stat().st_size  # Size in bytes | https://docs.python.org/3/library/os.html#os.stat_result

    if "modified" not in partial_record:
        partial_record["modified"] = Path(file_path).stat().st_mtime  # unix time stamp

    data: List = [hash for hash in partial_record["hash"] if hash["source"] == SourceType.DATA]
    partial_record["hash"] = data  # filter out other types ..

    if len(data) < 1:
        with open(file_path, mode="rb") as file:
            file_hash = hashlib.sha256(file.read())
            file_hex_digest: str = file_hash.hexdigest()
            partial_record["hash"].append({"source": SourceType.DATA, "type": "sha256", "value": file_hex_digest})

    return FileRecord(**partial_record)


def generate_file_list_hashes(base: Optional[Path] = None) -> None:
    if not base:
        base: Path = Path(".") / "hashes"

        with open("file_list.txt", mode="r", encoding="utf-8") as file:
            for line in tqdm(file):
                file_path: str = line.rstrip()
                file_path_hash: str = generate_file_path_hash(file_path=file_path)
                file_record_path: Path = base / f"{file_path_hash}.json"

                if file_record_path.exists():
                    with open(file_record_path.resolve().as_posix(), mode="r", encoding="utf-8") as file:
                        file_record: FileRecord = generate_hash(file_path=file_path, file_record=FileRecord(**json.load(file)))
                else:
                    file_record: FileRecord = generate_hash(file_path=file_path)

                with open(file_record_path.resolve().as_posix(), mode="w", encoding="utf-8") as file:
                    file.write(json.dumps(file_record.dict(exclude_unset=True), indent=4))


if __name__ == "__main__":
    generate_file_list_hashes()
