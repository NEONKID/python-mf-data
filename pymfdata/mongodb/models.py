from bson import ObjectId
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from typing import Generic, TypeVar


class BaseObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if ObjectId.is_valid(v) is False:
            raise TypeError('ObjectId invalid')
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


_T = TypeVar('_T', bound=BaseObjectId)


class BaseMongoDBModel(GenericModel, Generic[_T]):
    id: _T = Field(default_factory=_T, alias="_id")

    class Config:
        # allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


_MT = TypeVar('_MT', bound=BaseMongoDBModel)
