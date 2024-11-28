import os
import requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException

from ..models.integrations import Integrations


class Bling:

    def __init__(self, db_session: Session) -> None:
        self.__basic_auth = os.getenv("BLIG_BASIC_AUTH")
        self.db_session = db_session
        self.base_url = "https://api.bling.com.br/Api/v3"
        self.integration = None
        self.__access_token = self.refresh_token()

    def refresh_token(self) -> str:
        try:

            refresh_token = self.get_refresh_token()
        except NoResultFound:
            return

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
                .one()
            )
            self.integration = integration
            return integration.json_content.get("refresh_token")

        except NoResultFound as exc:
            raise exc

        except AttributeError as exc:
            raise exc

    def update_integration_info(self, data: dict, platform: str = "Bling") -> None:
        """
        Save updated integration information to the database.
        If no integration exists for the platform, create a new one.

        Args:
            data (dict): The new integration data to be saved.
            platform (str): The platform name to filter the integration data.

        Raises:
            Exception: If an unexpected error occurs.
        """
        try:
            if self.integration:
                self.integration.json_content = data

            else:
                integration = (
                    self.db_session.query(Integrations)
                    .filter(Integrations.platform == platform)
                    .one_or_none()
                )

                if integration is None:
                    integration = Integrations(
                        platform=platform,
                        json_content=data
                    )
                    self.db_session.add(integration)
                else:
                    integration.json_content = data

            self.db_session.commit()
        except Exception as exc:
            self.db_session.rollback()
            raise exc
