from datetime import date, datetime
from typing import Annotated, Literal, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator

Name = Annotated[str, Field(min_length=1, max_length=60)]
Revision = Annotated[int, Field(strict=True, ge=1)]
Status = Literal['available', 'reserved', 'sold']

class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Login(Input):
    username: str = Field(min_length=3, max_length=80)
    # Password whitespace is significant; override global trimming for this model.
    password: str = Field(min_length=1, max_length=128)
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=False)

class VehicleCreate(Input):
    make: Name
    model: str = Field(min_length=1, max_length=80)
    year: int = Field(strict=True, ge=1900, le=2100)
    price_pence: int = Field(strict=True, ge=0, le=100000000)
    approved_facts: list[Annotated[str, Field(min_length=1, max_length=200)]] = Field(default_factory=list, max_length=20)

class Edit(Input):
    revision: Revision

    @model_validator(mode='after')
    def changed_fields(self):
        changes = self.model_fields_set - {'revision'}
        if not changes or any(getattr(self, field) is None for field in changes):
            raise ValueError('Supply at least one changed field; null is not allowed.')
        return self

class VehicleEdit(Edit):
    make: Name | None = None
    model: Annotated[str, Field(min_length=1, max_length=80)] | None = None
    year: Annotated[int, Field(strict=True, ge=1900, le=2100)] | None = None
    price_pence: Annotated[int, Field(strict=True, ge=0, le=100000000)] | None = None
    approved_facts: Annotated[list[Annotated[str, Field(min_length=1, max_length=200)]], Field(max_length=20)] | None = None
    status: Status | None = None
    archived: Annotated[bool, Field(strict=True)] | None = None

class EnquiryCreate(Input):
    vehicle_id: Revision
    customer: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=1000)

class EnquiryEdit(Edit):
    status: Literal['new', 'contacted', 'closed']

class TaskCreate(Input):
    enquiry_id: Revision
    due_date: date
    note: str = Field(default='', max_length=300)

class TaskEdit(Edit):
    due_date: date | None = None
    note: Annotated[str, Field(max_length=300)] | None = None
    completed: Annotated[bool, Field(strict=True)] | None = None

class PhotoOutput(BaseModel):
    id: int
    vehicle_id: int
    caption: str
    credit: str
    source_url: str
    license: str
    license_url: str
    illustrative: bool
    is_cover: bool
    width: int
    height: int
    created_at: datetime

class RecordOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    revision: int
    created_at: datetime
    updated_at: datetime

class VehicleOutput(RecordOutput, VehicleCreate):
    status: Status
    archived: bool
    cover_photo_id: int | None = None
    photo_count: int = 0
    cover_photo: PhotoOutput | None = None

class EnquiryOutput(RecordOutput, EnquiryCreate):
    status: Literal['new', 'contacted', 'closed']

class TaskOutput(RecordOutput, TaskCreate):
    completed: bool

Item = TypeVar('Item')
class Page(BaseModel, Generic[Item]):
    items: list[Item]
    total: int
    offset: int
    limit: int

class UserOutput(BaseModel):
    id: int
    username: str
    role: Literal['viewer', 'sales', 'manager']

class Dashboard(BaseModel):
    available: int
    reserved: int
    sold: int
    stock_value_pence: int
    open_enquiries: int
    open_tasks: int
    overdue_tasks: int

class PhotoCreate(Input):
    revision: Revision
    data_url: str = Field(min_length=1, max_length=2800000)
    caption: str = Field(min_length=1, max_length=160)
    rights_confirmed: Literal[True]
    illustrative: bool = False
    credit: str = Field(default='', max_length=200)
    source_url: str = Field(default='', max_length=1000)
    license: str = Field(default='', max_length=100)
    license_url: str = Field(default='', max_length=1000)

    @field_validator('source_url', 'license_url')
    @classmethod
    def safe_link(cls, value):
        from urllib.parse import urlsplit
        if value:
            parts = urlsplit(value)
            if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password:
                raise ValueError('Use a public HTTPS source link.')
        return value

class CoverSelection(Input):
    revision: Revision

class PhotoSaved(BaseModel):
    photo: PhotoOutput
    vehicle_revision: int
