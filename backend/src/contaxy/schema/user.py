from datetime import datetime
from typing import Optional

from fastapi import Path
from pydantic import BaseModel, EmailStr, Field, SecretStr

USER_ID_PARAM = Path(
    ...,
    title="User ID",
    description="A valid user ID.",
    # TODO: add length restriction
)


class UserBase(BaseModel):
    username: Optional[str] = Field(
        None,
        example="john-doe",
        description="A unique username on the system.",
    )  # nickname
    email: Optional[EmailStr] = Field(
        None, example="john.doe@example.com", description="User email address."
    )
    disabled: Optional[bool] = Field(
        False,
        description="Indicates that user is disabled. Disabling a user will prevent any access to user-accesible resources.",
    )


class UserInput(UserBase):
    pass


class UserRegistration(UserInput):
    # The password is only part of the user input object and should never returned
    # TODO: a password can only be changed when used via oauth password bearer
    # TODO: System admin can change passwords for all users
    password: Optional[SecretStr] = Field(
        None,
        description="Password for the user. The password will be stored in as a hash.",
    )


class User(UserBase):
    id: Optional[str] = Field(
        None,
        example="16fd2706-8baf-433b-82eb-8c7fada847da",
        description="Unique ID of the user.",
    )
    technical_user: Optional[bool] = Field(
        False,
        description="Indicates if the user is a technical user created by the system.",
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Timestamp of the user creation. Assigned by the server and read-only.",
    )
