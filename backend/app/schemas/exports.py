"""Ordered export request/receipt. Membership and rendered revision need DB state."""
from typing import Literal
from pydantic import Field, UUID4, field_validator, model_validator
from .common import APIModel, Timestamp
from .pages import PageSnapshot


class ExportRequest(APIModel):
    pages: tuple[PageSnapshot,...] = Field(min_length=1, max_length=20)
    format: Literal['pdf','png','jpg'] = 'pdf'
    paper_size: Literal['a4'] = 'a4'
    orientation: Literal['auto','portrait','landscape'] = 'auto'
    margin_mm: float = Field(default=5, strict=True, ge=0, le=30)
    image_encoding: Literal['png','jpeg'] = 'png'

    @field_validator('pages')
    @classmethod
    def unique_pages(cls, value):
        if len({item.page_id for item in value})!=len(value):
            raise ValueError('Export không được trùng page ID.')
        return value

    @model_validator(mode='after')
    def one_image(self):
        if self.format!='pdf' and len(self.pages)!=1:
            raise ValueError('PNG/JPG xuất một trang; PDF cho nhiều trang.')
        return self


class ExportRead(APIModel):
    id: UUID4
    session_id: UUID4
    artifact_id: UUID4
    format: Literal['pdf','png','jpg']
    pages: tuple[PageSnapshot,...] = Field(min_length=1, max_length=20)
    created_at: Timestamp

    @model_validator(mode='after')
    def ordered_pages(self):
        if len({page.page_id for page in self.pages})!=len(self.pages):
            raise ValueError('Snapshot không được trùng page ID.')
        if self.format!='pdf' and len(self.pages)!=1:
            raise ValueError('Ảnh xuất chỉ có một trang.')
        return self
