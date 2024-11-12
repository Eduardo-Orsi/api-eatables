from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field, HttpUrl


class GUID(BaseModel):
    rendered: HttpUrl
    raw: HttpUrl

class Title(BaseModel):
    raw: str
    rendered: str

class Meta(BaseModel):
    inline_featured_image: bool

class Description(BaseModel):
    raw: str
    rendered: str

class Caption(BaseModel):
    raw: str
    rendered: str

class Size(BaseModel):
    file: str
    width: int
    height: int
    filesize: Optional[int] = None
    mime_type: str
    source_url: HttpUrl

class MediaDetails(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    file: Optional[str] = None
    filesize: Optional[int] = None
    sizes: dict[str, Size] = {}

    class ImageMeta(BaseModel):
        aperture: str
        credit: str
        camera: str
        caption: str
        created_timestamp: str
        copyright: str
        focal_length: str
        iso: str
        shutter_speed: str
        title: str
        orientation: str | int
        keywords: list[str]

    image_meta: Optional[ImageMeta] = None

class LinkItem(BaseModel):
    href: HttpUrl
    embeddable: Optional[bool] = None
    templated: Optional[bool] = None

class Links(BaseModel):
    self: list[LinkItem]
    collection: list[LinkItem]
    about: list[LinkItem]
    author: list[LinkItem]
    replies: list[LinkItem]
    wp_action_unfiltered_html: list[LinkItem] = Field(alias="wp:action-unfiltered-html")
    wp_action_assign_author: list[LinkItem] = Field(alias="wp:action-assign-author")
    curies: list[LinkItem]

class WordPressMediaResponse(BaseModel):
    id: int
    date: datetime
    date_gmt: datetime
    guid: GUID
    modified: datetime
    modified_gmt: datetime
    slug: str
    status: str
    type: str
    link: HttpUrl
    title: Title
    author: int
    featured_media: int
    comment_status: str
    ping_status: str
    template: str
    meta: Meta
    permalink_template: HttpUrl
    generated_slug: str
    class_list: list[str]
    description: Description
    caption: Caption
    alt_text: str
    media_type: str
    mime_type: str
    media_details: MediaDetails
    post: Optional[int]
    source_url: HttpUrl
    missing_image_sizes: list[Any]
    _links: Links

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
