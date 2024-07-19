import os
from datetime import datetime

import shopify
from dotenv import load_dotenv

from ..models.article import Post
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
        self.session = shopify.Session(store_url, api_version, access_token)
        shopify.ShopifyResource.activate_session(self.session)

    def add_article(self, post: Post) -> ShopifyArticleWrapper:
        shopify_article = self.convert_post_to_shopify_article(post)

        article = shopify.Article()
        article.activate_session(self.session)
        article.create({
            "items": [shopify_article.model_dump_json()]
        })
        json_response = article.to_dict()
        article.destroy()

        return json_response

    def convert_post_to_shopify_article(self, post: Post) -> ShopifyArticleWrapper:
        published_at = datetime.fromtimestamp(post.publication_date)

        blog = self.category_to_blog.get(post.category.name)
        if not blog:
            blog = 111765061939

        article_image = ArticleImage(src=post.featured_image.url, alt=post.featured_image.alt_text)
        shopify_article = ShopifyArticle(
            title=post.title,
            author="Eduardo Orsi",
            blog_id=blog,
            tags=None,
            body_html=post.content.html,
            published_at=published_at,
            image=article_image
        )

        return ShopifyArticleWrapper(article=shopify_article)
