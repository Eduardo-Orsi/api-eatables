import os
import base64
import json
from zoneinfo import ZoneInfo
from typing import Annotated, Optional
from contextlib import asynccontextmanager
from threading import Thread
from datetime import date, time, datetime, timezone, timedelta

import requests
from dotenv import load_dotenv
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, HTTPException, Request, Header, Response, Depends, Form, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .schema.yampi_event import YampiEvent
from .schema.article import PostWrapper
from .schema.love_cards_customer_schema import EmailRegsiter
from .integration.shopify import ShopifyIntegration
from .integration.bling import Bling
from .db.database import get_db, Base, engine
from .models.file import File
from .models.love_cards_customers import LoveCardsCustomer, LoveCardsAuth, generate_otc, send_email_otc
from .controller.relationship_event_controller import RelationshipController, RelationshipNotFound
from .controller.cron_job import sync_orders



load_dotenv()
SECRET_CODE = os.getenv("SECRET_CODE")
YAMPI_WEBHOOK_SIGNATURE = str(os.getenv("YAMPI_WEBHOOK_SIGNATURE"))
YAMPI_SHIPPING_SIGNATURE = str(os.getenv("YAMPI_SHIPPING_SIGNATURE"))
AUTOMARTICLES_TOKEN = os.getenv("AUTOMARTICLES_TOKEN")
BLING_CLIENT_ID = os.getenv("BLING_CLIENT_ID")
BLING_CLIENT_SECRET = os.getenv("BLING_CLIENT_SECRET")


app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "https://api-kangu.server.eatables.com.br",
    "https://lovesite.lovechocolate.com.br",
    "https://www.lovesite.lovechocolate.com.br",
    "https://love-cards-web.pages.dev/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")
Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()
trigger = CronTrigger(hour=12, minute=0, timezone=ZoneInfo("America/Sao_Paulo"))
scheduler.add_job(sync_orders, trigger)
scheduler.start()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    scheduler.shutdown()

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


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse(request=request, name="lp-love-site.html")



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


@app.get("/callback/bling/")
async def callback_bling(code: str, state: str, db: Session = Depends(get_db)):
    bling_auth_url = "https://api.bling.com.br/Api/v3/oauth/token"

    if state == "e720a99c3df96dc933eefc69074162ce":
        raise HTTPException(status_code=404, detail="Invalid State")

    credentials = f"{BLING_CLIENT_ID}:{BLING_CLIENT_SECRET}"
    basic_auth = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "1.0",
        "Authorization": f"Basic {basic_auth}",
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
    }

    response = requests.post(bling_auth_url, headers=headers, data=data, timeout=5)
    response_content = json.dumps(response.json())

    bling = Bling(db_session=db)
    bling.update_integration_info(data=response.json())

    return Response(content=response_content, media_type="application/json", status_code=response.status_code)


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

@app.get("/sync")
async def sync_method():
    thr = Thread(target=sync_orders)
    thr.start()
    return {"teste": "ok"}

@app.post("/love-cards/email")
async def register_email(email: EmailRegsiter, db: Session = Depends(get_db)):
    try:
        love_cards_customer = LoveCardsCustomer(email=email.email)
        db.add(love_cards_customer)
        db.commit()
        sucess_message = json.dumps({"message": "E-mail adicionado com sucesso!"})
        return Response(sucess_message, media_type="application/json", status_code=200)

    except IntegrityError as ex:
        raise HTTPException(status_code=200, detail="E-mail já está cadastrado") from ex
    except Exception as ex:
        print(ex.with_traceback())
        print(ex)
        raise HTTPException(status_code=400, detail="Erro ao registrar seu e-mail, tente novamente") from ex
 

@app.post("/love-cards/request-code")
async def request_login_code(cpf: str, db: Session = Depends(get_db)):
    # Find customer by CPF

    cleaned_cpf = cpf.replace(".", "").replace("-", "").strip().lower()
    customer = db.query(LoveCardsCustomer).filter(LoveCardsCustomer.cpf == cleaned_cpf).first()
    if not customer:
        raise HTTPException(status_code=404, detail="CPF não encontrado")

    # Generate new OTC
    code = generate_otc()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    auth = LoveCardsAuth(
        customer_id=customer.id,
        code=code,
        expires_at=expires_at
    )

    db.add(auth)
    db.commit()

    send_email_otc(code, customer.email)

    return {"message": f"Código enviado para o e-mail: {customer.email}"}


@app.post("/love-cards/validate-code")
async def validate_login_code(cpf: str, code: str, db: Session = Depends(get_db)):
    cleaned_cpf = cpf.replace(".", "").replace("-", "").strip().lower()
    customer = db.query(LoveCardsCustomer).filter(LoveCardsCustomer.cpf == cleaned_cpf).first()
    if not customer:
        raise HTTPException(status_code=404, detail="CPF não encontrado")

    auth = db.query(LoveCardsAuth).filter(
        and_(
            LoveCardsAuth.customer_id == customer.id,
            LoveCardsAuth.code == code,
            LoveCardsAuth.used == False,
            LoveCardsAuth.expires_at > datetime.now(timezone.utc)
        )
    ).first()

    if not auth:
        raise HTTPException(status_code=400, detail="Código inválido ou expirado")

    # Mark code as used
    auth.used = True
    db.commit()

    return {
        "message": "Login realizado com sucesso",
        "customer_id": str(customer.id)
    }
