from typing import List

from pydantic import BaseModel

from .hash_metadata import HashMetadata


class FileRecord(BaseModel):
    id: str
    path: str
    hash: List[HashMetadata]

    class Config:
        use_enum_values = True
