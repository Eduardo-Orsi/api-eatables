import os
from datetime import date, time
from typing import Annotated, Optional

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, HTTPException, Request, Header, Response, Depends, Form, UploadFile

from .schema.abandoned_cart import YampiEvent
from .schema.article import PostWrapper
from .integration.yampi import Yampi
from .integration.shopify import ShopifyIntegration
from .db.database import get_db, Base, engine
from .models.file import File
from .controller.relationship_event_controller import RelationshipController


load_dotenv()
SECRET_CODE = os.getenv("SECRET_CODE")
YAMPI_WEBHOOK_SIGNATURE = str(os.getenv("YAMPI_WEBHOOK_SIGNATURE"))
YAMPI_SHIPPING_SIGNATURE = str(os.getenv("YAMPI_SHIPPING_SIGNATURE"))
AUTOMARTICLES_TOKEN = os.getenv("AUTOMARTICLES_TOKEN")

app = FastAPI()
Base.metadata.create_all(bind=engine)

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


@app.post("/relationship/create/")
async def create_relationship(
    couple_name: str = Form(...),
    relationship_beginning_date: date = Form(...),
    relationship_beginning_hour: time = Form(...),
    message: str = Form(...),
    files: Optional[list[UploadFile]] = File(),
    db: Session = Depends(get_db)
):
    return await RelationshipController.add_relationship_event(
        db=db,
        couple_name=couple_name,
        relationship_beginning_date=relationship_beginning_date,
        relationship_beginning_hour=relationship_beginning_hour,
        message=message,
        files=files
    )
