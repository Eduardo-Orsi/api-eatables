import os
from datetime import date, time
from typing import Annotated, Optional

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, HTTPException, Request, Header, Response, Depends, Form, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .schema.yampi_event import YampiEvent
from .schema.article import PostWrapper
from .integration.yampi import Yampi
from .integration.shopify import ShopifyIntegration
from .db.database import get_db, Base, engine
from .models.file import File
from .controller.relationship_event_controller import RelationshipController, RelationshipNotFound



load_dotenv()
SECRET_CODE = os.getenv("SECRET_CODE")
YAMPI_WEBHOOK_SIGNATURE = str(os.getenv("YAMPI_WEBHOOK_SIGNATURE"))
YAMPI_SHIPPING_SIGNATURE = str(os.getenv("YAMPI_SHIPPING_SIGNATURE"))
AUTOMARTICLES_TOKEN = os.getenv("AUTOMARTICLES_TOKEN")

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")
Base.metadata.create_all(bind=engine)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"\nValidation error: {exc}\n")
    raise HTTPException(status_code=422, detail=exc.errors())


@app.exception_handler(RelationshipNotFound)
async def unicorn_exception_handler(request: Request, exc: RelationshipNotFound):
    
    if exc.redirect_url:
        return RedirectResponse(url=exc.redirect_url, status_code=304)
    
    return HTMLResponse(
        status_code=404,
        content=f"<h1>{exc.error_message}</h1>",
    )


@app.get("/")
async def main():
    return RedirectResponse(url="/create/", status_code=301)


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
async def webhook_yampi(yampi_event: YampiEvent, request: Request,
                        x_yampi_hmac_sha256: Annotated[str | None, Header()] = None,
                        db: Session = Depends(get_db)):
    # body = await request.body()
    # await Yampi.validate_webhook_signature(body,
    #                                     x_yampi_hmac_sha256,
    #                                     YAMPI_WEBHOOK_SIGNATURE)

    await RelationshipController.mark_as_paid(db, yampi_event)

    return yampi_event


@app.get("/create/", response_class=HTMLResponse)
async def sales_page(request: Request):
    return templates.TemplateResponse(request=request, name="forms.html")


@app.get("/{small_id}/{slug}", response_class=HTMLResponse)
async def relationship_page(request: Request, small_id: str, slug: str, db: Session = Depends(get_db)):
    context = await RelationshipController.get_relationship_event(db, small_id)
    return templates.TemplateResponse(request=request, context=context, name="relationship.html")


@app.post("/relationship/create/")
async def create_relationship(
    email: str = Form(...),
    couple_name: str = Form(...),
    relationship_beginning_date: date = Form(...),
    relationship_beginning_hour: time = Form(...),
    message: str = Form(...),
    plan: str = Form(...),
    files: Optional[list[UploadFile]] = File(),
    db: Session = Depends(get_db)
):
    return await RelationshipController.add_relationship_event(
        db=db,
        couple_name=couple_name,
        relationship_beginning_date=relationship_beginning_date,
        relationship_beginning_hour=relationship_beginning_hour,
        message=message,
        plan=plan,
        email=email,
        files=files
    )
