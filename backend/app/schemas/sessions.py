"""Document sessions and ordered export snapshots; no routes implemented here."""
from pydantic import Field, StrictInt, UUID4, field_validator, model_validator

from .common import APIModel, Timestamp
from .pages import PageRead
from .exports import ExportRequest  # keep the pre-11.01 import path compatible


class SessionCreate(APIModel):
    title: str = Field(default='Tài liệu chưa đặt tên', strict=True, min_length=1, max_length=200)

    @field_validator('title', mode='before')
    @classmethod
    def trim_title(cls, value):
        return value.strip() if isinstance(value,str) else value


class SessionRename(SessionCreate):
    title: str = Field(strict=True, min_length=1, max_length=200)


class SessionRead(APIModel):
    id: UUID4
    title: str = Field(strict=True, min_length=1, max_length=200)
    created_at: Timestamp
    updated_at: Timestamp


class SessionDetail(SessionRead):
    pages: tuple[PageRead,...] = ()

    @model_validator(mode='after')
    def ordered_members(self):
        if any(page.session_id!=self.id for page in self.pages):
            raise ValueError('Trang không thuộc tài liệu.')
        ids = [page.id for page in self.pages]
        positions = [page.position for page in self.pages]
        if len(ids)>20 or len(ids)!=len(set(ids)) or positions!=sorted(set(positions)):
            raise ValueError('Pages phải duy nhất và theo position tăng dần, tối đa20.')
        return self


class SessionList(APIModel):
    items: tuple[SessionRead,...]
    limit: StrictInt = Field(ge=1, le=100)
    offset: StrictInt = Field(ge=0)
    total: StrictInt = Field(ge=0)


class PageOrderRequest(APIModel):
    page_ids: tuple[UUID4,...] = Field(max_length=20)

    @field_validator('page_ids')
    @classmethod
    def unique_pages(cls, value):
        if len(set(value))!=len(value):
            raise ValueError('Page IDs không được trùng.')
        return value


