from enum import Enum
from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel, Field

from contaxy.schema.deployment import Service, ServiceInput
from contaxy.schema.shared import QUALIFIED_RESOURCE_ID_REGEX

CORE_EXTENSION_ID = "core"
GLOBAL_EXTENSION_PROJECT = "ctxy-global"

EXTENSION_ID_PARAM = Query(
    None,
    title="Extension ID",
    description="Extension ID. If not specified, the system will decide. Use `core` to explicitly select the core platform.",
    regex=QUALIFIED_RESOURCE_ID_REGEX,
)


class ExtensionType(str, Enum):
    USER_EXTENSION = "user-extension"
    PROJECT_EXTENSION = "project-extension"


class ExtensionBase(BaseModel):
    capabilities: Optional[List[str]] = Field(
        None,
        # TODO: provide example
        description="List of capabilities implemented by this extension.",
    )
    api_extension_endpoint: Optional[str] = Field(
        None,
        example="8080/extension/api",
        description="The endpoint base URL that implements the API operation stated in the capabilities property.",
    )
    ui_extension_endpoint: Optional[str] = Field(
        None,
        example="8080/webapp/ui",
        description="The endpoint instruction that provide a Web UI. If this is provided, the extension will be integrated into the UI.",
    )
    extension_type: Optional[ExtensionType] = Field(
        None,
        example=ExtensionType.PROJECT_EXTENSION,
        description="The type of the extension.",
    )


class ExtensionInput(ServiceInput, ExtensionBase):
    pass


class Extension(Service, ExtensionBase):
    pass
