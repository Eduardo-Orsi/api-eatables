import os
import json
from datetime import datetime

import requests
from dotenv import load_dotenv

from ..models.article import PostWrapper
from ..models.shopify_article import ShopifyArticle, ShopifyArticleWrapper, ArticleImage


load_dotenv()
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")


class ShopifyIntegration:

    category_to_blog = {
       "Afrodisíacos": 100344561971,
       "Casal": 111747006771,
       "Casamento": 111747039539,
       "Dicas": 111765061939,
       "Dicas Relacionamento": 111765094707,
       "Experiências": 111765160243,
       "Namoro": 111498985779,
       "Natural": 111747072307,
       "Receitas": 111765225779,
       "Relacionamento": 109790396723,
       "Rotina": 111499149619,
       "Saúde": 111747105075
    }

    def __init__(self, store_url: str, api_version: str, access_token: str = SHOPIFY_ACCESS_TOKEN) -> None:
        self.api_version = api_version
        self.store_url = store_url
        self.access_token = access_token

    async def add_article(self, post_wrapper: PostWrapper) -> ShopifyArticleWrapper:
        shopify_article = self.convert_post_to_shopify_article(post_wrapper)

        blog = self.category_to_blog.get(post_wrapper.post.category.name)
        if not blog:
            blog = 111765061939

        url = f"{self.store_url}admin/api/{self.api_version}/blogs/{blog}/articles.json"
        headers = {"X-Shopify-Access-Token": self.access_token, 'Content-Type': 'application/json'}
        payload = json.dumps(shopify_article.model_dump())
        response = requests.post(url=url, headers=headers, data=payload, timeout=5)

        print(f"POST: {post_wrapper.event} - STATUS: {response.status_code}")
        print(f"PUBLISHED AT: {shopify_article.article.published_at} - PUBLISHED: {shopify_article.article.published}")

        return response.json()

    def convert_post_to_shopify_article(self, post_wrapper: PostWrapper) -> ShopifyArticleWrapper:
        published_at = datetime.fromtimestamp(post_wrapper.post.publication_date).strftime("%a %b %d %H:%M:%S UTC %Y")

        article_image = ArticleImage(src=post_wrapper.post.featured_image.url.unicode_string(),
                                     alt=post_wrapper.post.featured_image.alt_text)

        shopify_article = ShopifyArticle(
            title=post_wrapper.post.title,
            author="Eduardo Orsi",
            tags=None,
            body_html=post_wrapper.post.content.html,
            published_at=published_at,
            handle=post_wrapper.post.slug,
            summary_html=post_wrapper.post.description,
            published=False,
            image=article_image
        )

        return ShopifyArticleWrapper(article=shopify_article)
