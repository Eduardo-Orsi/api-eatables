from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class MergeFields(BaseModel):
    FNAME: str
    LNAME: str
    PHONE: str
    ADDRESS: Optional[str]


class Tags(BaseModel):
    id: int
    name: str


class MailchimpMember(BaseModel):
    email_address: str
    status: str
    merge_fields: MergeFields
    language: str
    ip_signup: str
    timestamp_signup: datetime
    timestamp_opt: datetime
    ip_opt: str
    tags: list[str]
