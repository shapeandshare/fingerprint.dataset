from pydantic import BaseModel

from ..source_type import SourceType


class HashMetadata(BaseModel):
    source: SourceType
    type: str
    value: str
