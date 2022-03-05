import hashlib
import json
import uuid
from pathlib import Path
from typing import List

from tqdm import tqdm

from contracts.dtos.file_record import FileRecord
from contracts.source_type import SourceType


def serialize_file_data(files: List[FileRecord]) -> List:
    raw_list: List = []
    for file_obj in files:
        raw_list.append(file_obj.dict(exclude_unset=True))
    return raw_list


def load_data() -> List:
    with open("../file_list.json", mode="r", encoding="utf-8") as file:
        return json.load(file)


def generate_file_path_hash(file_path: str) -> str:
    filename_hash = hashlib.sha256(file_path.encode())
    return filename_hash.hexdigest()


def generate_hash(file_path: str) -> FileRecord:
    with open(file_path, mode="rb") as file:
        filename_hash = hashlib.sha256(file_path.encode())
        filename_hash_hex_digest: str = filename_hash.hexdigest()

        file_hash = hashlib.sha256(file.read())
        file_hex_digest: str = file_hash.hexdigest()
        return FileRecord(
            **{
                "id": str(uuid.uuid4()),
                "path": file_path,
                "hash": [
                    {"source": SourceType.DATA, "type": "sha256", "value": file_hex_digest},
                    {"source": SourceType.NAME, "type": "sha256", "value": filename_hash_hex_digest},
                ],
            }
        )


def generate_file_list_hashes() -> None:
    output_base: Path = Path("../..") / "hashes"

    file_list: List[str] = load_data()
    for file_path in tqdm(file_list):
        file_path_hash: str = generate_file_path_hash(file_path=file_path)
        file_record_path: Path = output_base / f"{file_path_hash}.json"

        if not file_record_path.exists():
            file_record: FileRecord = generate_hash(file_path=file_path)

            with open(file_record_path.resolve().as_posix(), mode="w", encoding="utf-8") as file:
                file.write(json.dumps(file_record.dict(exclude_unset=True), indent=4))


if __name__ == "__main__":
    generate_file_list_hashes()
