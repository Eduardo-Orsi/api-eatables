import base64
import urllib.parse

import httpx
from fastapi import UploadFile
from fastapi.exceptions import HTTPException
from pydantic import ValidationError

from ..schema.wordpress_file import WordPressMediaResponse


class WordPress:

    def __init__(self, wp_username: str, wp_app_password: str, wp_api_url: str) -> None:
        self.__wp_username = wp_username
        self.__wp_app_password = wp_app_password
        self.__wp_api_url = wp_api_url
        self.__wp_credentials = f"{self.__wp_username}:{self.__wp_app_password}"
        self.__wp_token = base64.b64encode(self.__wp_credentials.encode()).decode()

    async def upload_file(self, upload_file: UploadFile) -> WordPressMediaResponse:

        if not upload_file:
            return

        headers = {
            'Authorization': f'Basic {self.__wp_token}',
        }

        async with httpx.AsyncClient() as client:
            try:
                contents = await upload_file.read()
                file_name = upload_file.filename
                mime_type = upload_file.content_type

                wp_headers = headers.copy()
                wp_headers.update({
                    'Content-Disposition': f'attachment; filename="{urllib.parse.quote(file_name)}"',
                    'Content-Type': mime_type,
                })

                response = await client.post(
                    f"{self.__wp_api_url}wp-json/wp/v2/media",
                    headers=wp_headers,
                    content=contents,
                    timeout=10
                )

                if response.status_code == 201:
                    try:
                        return WordPressMediaResponse(**response.json())
                    except ValidationError as exc:
                        raise exc

                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Failed to upload file '{file_name}' to WordPress: {response.text}"
                    )
            except Exception as e:
                raise e
