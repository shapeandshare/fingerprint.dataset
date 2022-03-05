from pydantic import BaseModel

from contracts.source_type import SourceType


class HashMetadata(BaseModel):
    source: SourceType
    type: str
    value: str
