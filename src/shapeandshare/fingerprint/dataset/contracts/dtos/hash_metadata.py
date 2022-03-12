""" Hash Metadata Definition"""

from ..source_type import SourceType
from .base_model import BaseModel


# pylint: disable=no-name-in-module,too-few-public-methods
class HashMetadata(BaseModel):
    """
    HashMetadata DTO

    Attributes
    ----------
    source: SourceType
    type: str
    value: str
    """

    source: SourceType
    type: str
    value: str
