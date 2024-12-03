import os
import requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from ..models.integrations import Integrations
from ..models.orders_synced import SyncedOrder


class Bling:

    def __init__(self, db_session: Session) -> None:
        self.__basic_auth = os.getenv("BLIG_BASIC_AUTH")
        self.db_session = db_session
        self.base_url = "https://api.bling.com.br/Api/v3"
        self.__access_token = self.refresh_token()
        self.__auth_header = {
            "Authorization": f"Bearer {self.__access_token}"
        }


    def refresh_token(self) -> str:

        refresh_token = self.get_refresh_token()

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        headers = {
            "Authorization": f"Basic {self.__basic_auth}="
        }

        response = requests.post(f"{self.base_url}/oauth/token", headers=headers, data=data, timeout=5)

        if response.status_code != 200:
            return None

        response_data = response.json()
        self.update_integration_info(data=response_data)
        print("TOKEN BLING SUCESSO")

        return response_data["access_token"]

    def get_refresh_token(self, platform: str = "Bling") -> str:
        """
        Retrieve the refresh token from the database.

        Args:
            platform (str): The platform name to filter the integration data.

        Returns:
            str: The refresh token for the platform.

        Raises:
            ValueError: If the refresh token is not found.
        """
        try:
            integration = (
                self.db_session.query(Integrations)
                .filter(Integrations.platform == platform)
                .first()
            )
            return integration.json_content.get("refresh_token")

        except NoResultFound as exc:
            raise exc

        except AttributeError as exc:
            raise exc

    def update_integration_info(self, data: dict, platform: str = "Bling") -> None:
        """
        Save updated integration information to the database.
        If no integration exists for the platform, do nothing.

        Args:
            data (dict): The new integration data to be saved.
            platform (str): The platform name to filter the integration data.

        Raises:
            Exception: If an unexpected error occurs.
        """
        try:
            integration_data = (
                self.db_session.query(Integrations)
                .filter(Integrations.platform == platform)
                .update({
                    'json_content': data
                })
            )
            self.db_session.commit()

        except Exception as exc:
            self.db_session.rollback()
            raise exc


    def get_orders(self, number_of_orders: int = 100) -> dict:
        response = requests.get(
            f"{self.base_url}/pedidos/vendas?pagina=1&limite={number_of_orders}&idsSituacoes[]=9&idLoja=204726940",
            headers=self.__auth_header,
            timeout=5
        )

        if not response.status_code == 200:
            return
        return response.json()

    def get_order(self, order_id: int | str) -> dict:
        response = requests.get(f"{self.base_url}/pedidos/vendas/{order_id}", headers=self.__auth_header, timeout=5)

        if not response.status_code == 200:
            return
        return response.json()

    def is_order_synced(self, bling_order_id: int):
        return self.db_session.query(SyncedOrder).filter_by(bling_order_id=bling_order_id).first() is not None

    def mark_order_as_synced(self, bling_order_id: int, yampi_id: str, shopify_order_id: str, tracking_code: str, tracking_url: str, tracking_campany: str):
        synced_order = SyncedOrder(
            bling_order_id=bling_order_id,
            synced=True,
            yampi_id=yampi_id,
            shopify_order_id=shopify_order_id,
            tracking_code=tracking_code,
            tracking_url=tracking_url,
            tracking_campany=tracking_campany
        )
        self.db_session.add(synced_order)
        self.db_session.commit()
