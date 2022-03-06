from typing import List, Optional

from pydantic import BaseModel

from .hash_metadata import HashMetadata


class FileRecord(BaseModel):
    size: Optional[int]
    modified: Optional[str]
    path: str
    hash: List[HashMetadata]

    class Config:
        use_enum_values = True
