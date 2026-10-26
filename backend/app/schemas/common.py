"""JSON boundary conventions; no storage or HTTP side effects."""
from datetime import UTC
from typing import Annotated, Literal

from pydantic import AfterValidator, AwareDatetime, BaseModel, ConfigDict, Field, StrictInt

Timestamp = Annotated[AwareDatetime, AfterValidator(lambda value: value.astimezone(UTC))]
Revision = Annotated[StrictInt, Field(ge=0)]
Milliseconds = Annotated[float, Field(strict=True, ge=0)]
ArtifactKind = Literal['original','normalized','thumbnail','render','preview','debug','pdf','export_image']


class APIModel(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, allow_inf_nan=False)
