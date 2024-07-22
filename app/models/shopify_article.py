from typing import Optional

from pydantic import BaseModel


class ArticleImage(BaseModel):
    src: str
    alt: str


class ShopifyArticle(BaseModel):
    title: str
    author: str
    tags: Optional[str]
    body_html: str
    published_at: str
    handle: str
    summary_html: str
    image: ArticleImage


class ShopifyArticleWrapper(BaseModel):
    article: ShopifyArticle
