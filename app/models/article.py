from pydantic import BaseModel, HttpUrl


class Content(BaseModel):
    text: str
    html: str
    rich: str


class FeaturedImage(BaseModel):
    url: HttpUrl
    filename: str
    alt_text: str


class Category(BaseModel):
    id: str
    name: str


class Post(BaseModel):
    id: str
    slug: str
    status: str
    title: str
    content: Content
    description: str
    featured_image: FeaturedImage
    category: Category
    publication_date: int


class PostWrapper(BaseModel):
    event: str
    post: Post


class AutomarticlesCheck(BaseModel):
    event: str
