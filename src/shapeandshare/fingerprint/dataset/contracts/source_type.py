""" Source Type Definition """

from enum import Enum


class SourceType(str, Enum):
    """SourceType Enumeration"""

    NAME = "name"
    DATA = "data"
