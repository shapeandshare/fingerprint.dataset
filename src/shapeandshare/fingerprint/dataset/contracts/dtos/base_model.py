""" BaseModel Definition """

# pylint: disable=no-name-in-module,too-few-public-methods
from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    """Base Model DTO"""

    class Config:
        """Global Config"""

        arbitrary_types_allowed = True
        use_enum_values = True
        validate_assignment = True
