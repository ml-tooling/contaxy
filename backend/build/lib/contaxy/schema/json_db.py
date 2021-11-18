from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JsonDocument(BaseModel):
    key: str = Field(
        ...,
        example="my-json-document",
        description="Unique key of the document.",
    )
    json_value: str = Field(
        ...,
        example="{'foo': 'bar'}",
        description="JSON value of the document.",
    )
    created_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Creation date of the document.",
    )
    created_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that created this document.",
    )
    updated_at: Optional[datetime] = Field(
        None,
        example="2021-04-23T10:20:30.400+02:30",
        description="Last date at which the document was updated.",
    )
    updated_by: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="ID of the user that has last updated this document.",
    )
