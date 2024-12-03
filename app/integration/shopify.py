import os
import json
from datetime import datetime
from typing import Optional

import requests
from dotenv import load_dotenv

from ..schema.article import PostWrapper
from ..schema.shopify_article import ShopifyArticle, ShopifyArticleWrapper, ArticleImage

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
        self.store_url = store_url.rstrip('/')
        self.access_token = access_token
        self.graphql_url = f"{self.store_url}/admin/api/{self.api_version}/graphql.json"
        self.headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': self.access_token
        }

    def add_tracking_code(self, order_id: str, tracking_company: str, tracking_number: str, tracking_url: str) -> None:
        # Get the fulfillment orders for the order
        fulfillment_orders = self.get_fulfillment_orders(order_id)
        if fulfillment_orders:
            # Loop through each fulfillment order and create a fulfillment
            for fulfillment_order in fulfillment_orders:
                fulfillment_order_id = fulfillment_order['id']
                success = self.create_fulfillment(
                    fulfillment_order_id=fulfillment_order_id,
                    tracking_company=tracking_company,
                    tracking_number=tracking_number,
                    tracking_url=tracking_url,
                    notify_customer=False
                )
                if success:
                    print(f"Fulfillment created successfully for Fulfillment Order ID: {fulfillment_order_id}")
                else:
                    print(f"Failed to create fulfillment for Fulfillment Order ID: {fulfillment_order_id}")
        else:
            print('No fulfillment orders found for this order.')

    def get_fulfillment_orders(self, order_id: str) -> list:
        query = '''
        query GetFulfillmentOrders($orderId: ID!) {
            order(id: $orderId) {
                id
                fulfillmentOrders(first: 10) {
                    edges {
                        node {
                            id
                            status
                            lineItems(first: 10) {
                                edges {
                                    node {
                                        id
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        '''
        variables = {
            "orderId": f"gid://shopify/Order/{order_id}"
        }
        response = requests.post(
            self.graphql_url,
            headers=self.headers,
            json={'query': query, 'variables': variables},
            timeout=5
        )
        result = response.json()
        if 'errors' in result:
            print('Errors:', result['errors'])
            return None
        else:
            fulfillment_orders = [
                edge['node'] for edge in result['data']['order']['fulfillmentOrders']['edges']
            ]
            return fulfillment_orders

    def create_fulfillment(self, fulfillment_order_id: str, tracking_company: str, tracking_number: str, tracking_url: str, notify_customer: bool = False) -> bool:
        
        line_items = self.get_fulfillment_order_line_items(fulfillment_order_id)
        if not line_items:
            print(f"## No line items to fulfill for Fulfillment Order ID: {fulfillment_order_id}")
            return False
        
        mutation = '''
        mutation fulfillmentCreateV2($fulfillment: FulfillmentV2Input!) {
            fulfillmentCreateV2(fulfillment: $fulfillment) {
                fulfillment {
                    id
                    status
                    trackingInfo {
                        number
                        url
                    }
                }
                userErrors {
                    field
                    message
                }
            }
        }
        '''
        variables = {
            "fulfillment": {
                "notifyCustomer": notify_customer,
                "trackingInfo": {
                    "company": tracking_company,
                    "number": tracking_number,
                    "url": tracking_url
                },
                "lineItemsByFulfillmentOrder": [
                    {
                        "fulfillmentOrderId": fulfillment_order_id,
                        # Here we are fulfilling all line items in the fulfillment order
                        "fulfillmentOrderLineItems": [
                            {
                                "id": line_item['id'],
                                "quantity": line_item['quantity']
                            } for line_item in self.get_fulfillment_order_line_items(fulfillment_order_id)
                        ]
                    }
                ]
            }
        }
        response = requests.post(
            self.graphql_url,
            headers=self.headers,
            json={'query': mutation, 'variables': variables},
            timeout=5
        )
        result = response.json()
        if 'errors' in result:
            print('Errors:', result['errors'])
            return False
        else:
            data = result['data']['fulfillmentCreateV2']
            if data['userErrors']:
                print('User Errors:', data['userErrors'])
                return False
            else:
                return True

    def get_fulfillment_order_line_items(self, fulfillment_order_id: str) -> list:
        query = '''
            query GetFulfillmentOrderLineItems($fulfillmentOrderId: ID!) {
                node(id: $fulfillmentOrderId) {
                    ... on FulfillmentOrder {
                        lineItems(first: 10) {
                            edges {
                                node {
                                    id
                                    remainingQuantity
                                }
                            }
                        }
                    }
                }
            }
        '''
        variables = {
            "fulfillmentOrderId": fulfillment_order_id
        }
        response = requests.post(
            self.graphql_url,
            headers=self.headers,
            json={'query': query, 'variables': variables},
            timeout=5
        )
        result = response.json()
        if 'errors' in result:
            print('Errors:', result['errors'])
            return []
        else:
            line_items = [
                {
                    'id': edge['node']['id'],
                    'quantity': edge['node']['remainingQuantity']
                }
                for edge in result['data']['node']['lineItems']['edges']
                if edge['node']['remainingQuantity'] > 0
            ]
            return line_items

        
    def get_order_id_by_name(self, order_name: str) -> Optional[str]:
        query = '''
        query getOrderByName($query: String!) {
            orders(first: 1, query: $query) {
                edges {
                    node {
                        id
                        name
                    }
                }
            }
        }
        '''
        variables = {
            "query": f"name:{order_name}"
        }
        response = requests.post(
            self.graphql_url,
            headers=self.headers,
            json={'query': query, 'variables': variables},
            timeout=5
        )
        result = response.json()
        if 'errors' in result:
            print('Errors:', result['errors'])
            return None
        else:
            orders = result['data']['orders']['edges']
            if orders:
                order_id = orders[0]['node']['id']
                order_id = order_id.split('/')[-1]
                return order_id
            else:
                print(f"No order found with name {order_name}")
                return None


    async def add_article(self, post_wrapper: PostWrapper) -> ShopifyArticleWrapper:
        # Existing method remains unchanged
        shopify_article = self.convert_post_to_shopify_article(post_wrapper)

        blog = self.category_to_blog.get(post_wrapper.post.category.name)
        if not blog:
            blog = 111765061939

        url = f"{self.store_url}/admin/api/{self.api_version}/blogs/{blog}/articles.json"
        headers = {"X-Shopify-Access-Token": self.access_token, 'Content-Type': 'application/json'}
        payload = json.dumps(shopify_article.model_dump())
        response = requests.post(url=url, headers=headers, data=payload, timeout=5)

        return response.json()

    def convert_post_to_shopify_article(self, post_wrapper: PostWrapper) -> ShopifyArticleWrapper:
        # Existing method remains unchanged
        published_at = datetime.fromtimestamp(post_wrapper.post.publication_date).strftime("%a %b %d %H:%M:%S UTC %Y")

        article_image = ArticleImage(
            src=post_wrapper.post.featured_image.url.unicode_string(),
            alt=post_wrapper.post.featured_image.alt_text
        )

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
