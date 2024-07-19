from typing import Optional
from datetime import datetime

from pydantic import BaseModel, HttpUrl


class ArticleImage(BaseModel):
    src: HttpUrl
    alt: str


class ShopifyArticle(BaseModel):
    title: str
    author: str
    blog_id: int
    tags: Optional[str]
    body_html: str
    published_at: datetime
    image: ArticleImage


class ShopifyArticleWrapper(BaseModel):
    article: ShopifyArticle
