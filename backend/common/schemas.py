from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict


class BaseSelectSchema(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        from_attributes=True,
    )


class BaseSchema(BaseModel):
    class FieldNames:
        pass

    fields: ClassVar[Any] = FieldNames

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        fields = type("fields", (), {})
        for name in cls.model_fields:
            setattr(fields, name, name)

        cls.fields = fields
