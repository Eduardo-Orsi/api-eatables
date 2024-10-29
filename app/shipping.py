import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, HTTPException, Request, Header, Response

from .schema.abandoned_cart import YampiEvent
from .schema.article import PostWrapper
from .integration.yampi import Yampi
from .integration.shopify import ShopifyIntegration


load_dotenv()
SECRET_CODE = os.getenv("SECRET_CODE")
YAMPI_WEBHOOK_SIGNATURE = str(os.getenv("YAMPI_WEBHOOK_SIGNATURE"))
YAMPI_SHIPPING_SIGNATURE = str(os.getenv("YAMPI_SHIPPING_SIGNATURE"))
AUTOMARTICLES_TOKEN = os.getenv("AUTOMARTICLES_TOKEN")


app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # print(f"\nValidation error: {exc}\n")
    raise HTTPException(status_code=422, detail=exc.errors())

@app.post("/webhook/automarticles/article/")
async def webhook_article(post_wrapper: PostWrapper, access_token: Annotated[str | None, Header()] = None):

    if not access_token == AUTOMARTICLES_TOKEN:
        raise HTTPException(status_code=404, detail="Access Token not found")

    if post_wrapper.event == "CHECK_INTEGRATION":
        return {"token": AUTOMARTICLES_TOKEN}

    shopify = ShopifyIntegration("https://de9306.myshopify.com/", "2024-01")

    if post_wrapper.event in ["POST_UPDATED"] and post_wrapper.post.status == "publish":
        return await shopify.add_article(post_wrapper)
    return Response({}, status_code=200)


@app.post("/webhook/yampi/")
async def webhook_yampi(yampi_event: YampiEvent, request: Request, x_yampi_hmac_sha256: Annotated[str | None, Header()] = None):
    body = await request.body()
    await Yampi.validate_webhook_signature(body,
                                        x_yampi_hmac_sha256,
                                        YAMPI_WEBHOOK_SIGNATURE)

    return yampi_event
