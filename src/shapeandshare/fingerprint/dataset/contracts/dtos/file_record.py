""" File Record Definition """

from typing import Optional

from .base_model import BaseModel
from .hash_metadata import HashMetadata


# pylint: disable=no-name-in-module,too-few-public-methods
class FileRecord(BaseModel):
    """
    FileRecord DTO

    Attributes
    ----------
    size: Optional[int]
    modified: Optional[str]
    path: str
    hash: list[HashMetadata]
    """

    size: Optional[int]
    modified: Optional[str]
    path: str
    hash: list[HashMetadata]
