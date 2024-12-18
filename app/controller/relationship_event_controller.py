import os
import threading
from typing import Optional
from datetime import date, time

from fastapi import UploadFile, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from pydantic import ValidationError

from ..models.file import File
from ..models.relationship_event import RelationshipEvent
from ..models.love_cards_customers import LoveCardsCustomer
from ..schema.relationship_event_schema import RelationshipEventForm
from ..schema.yampi_event import YampiEvent
from ..integration.wordpress import WordPress
from ..integration.office_365_mailer import EmailSender
from ..utils.url_helper import slugfy
from ..db.database import not_async_get_db


WP_API_URL = os.getenv("WP_API_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

AZURE_APPLICATION_ID = os.getenv("AZURE_APPLICATION_ID")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_SECRET_VALUE = os.getenv("AZURE_CLIENT_SECRET_VALUE")


class RelationshipNotFound(Exception):
    def __init__(self, error_message: str, redirect_url: str = None):
        self.error_message = error_message
        self.redirect_url = redirect_url


class RelationshipController:

    @staticmethod
    async def add_relationship_event(db: Session, couple_name: str, relationship_beginning_date: date, email: str,
                               relationship_beginning_hour: time, message: str, plan: str, files: Optional[list[UploadFile]]):

        try:
            relationship_event_schema = RelationshipEventForm(
                couple_name=couple_name,
                relationship_beginning_date=relationship_beginning_date,
                relationship_beginning_hour=relationship_beginning_hour,
                plan=plan,
                email=email,
                paid=False,
                message=message
            )
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=e.errors())

        relationship_event = RelationshipEvent(
            email=relationship_event_schema.email,
            couple_name=relationship_event_schema.couple_name,
            relationship_beginning_date=relationship_event_schema.relationship_beginning_date,
            relationship_beginning_hour=relationship_event_schema.relationship_beginning_hour,
            message=relationship_event_schema.message,
            couple_slug=slugfy(relationship_event_schema.couple_name),
            plan=relationship_event_schema.plan.name,
            paid=relationship_event_schema.paid
        )
        db.add(relationship_event)
        db.commit()

        wp_site = WordPress(WP_USERNAME, WP_APP_PASSWORD, WP_API_URL)
        for file in files:
            file_bytes = await file.read()
            file_upload_thr = threading.Thread(target=RelationshipController.save_files, args=(db, wp_site, relationship_event.id, file, file_bytes))
            file_upload_thr.start()

        user_email = relationship_event_schema.email

        if relationship_event_schema.plan.name == "SIMPLE":
            return RedirectResponse(status_code=301, url=f"https://seguro.lovechocolate.com.br/r/AMDUAUSCKJ?utm_campaign={user_email}&utm_source={user_email}")
        return RedirectResponse(status_code=301, url=f"https://seguro.lovechocolate.com.br/r/RFXUL7Z028?utm_campaign={user_email}&utm_source={user_email}") 

    @staticmethod
    def save_files(db: Session, wp: WordPress, relations_ship_id: Column[UUID], file: UploadFile, file_bytes: bytes) -> None:
        db = not_async_get_db()
        uploaded_file = wp.upload_file(file, file_bytes)
        file_record = File(
            relationship_event_id=relations_ship_id,
            filename=uploaded_file.title.rendered,
            content_type=uploaded_file.mime_type,
            url=uploaded_file.source_url.unicode_string(),
            wordpress_id=uploaded_file.id
        )
        db.add(file_record)
        db.commit()
        print(f"Arquivo Importador com Sucesso: {file_record.filename}")

    @staticmethod
    async def get_relationship_event(db: Session, small_id: str) -> dict:
        relationship_event = db.query(RelationshipEvent).filter(RelationshipEvent.small_id == small_id).first()
        if not relationship_event:
            raise RelationshipNotFound(error_message="Página não encontrada", redirect_url="/create/")

        if not relationship_event.paid:
            raise RelationshipNotFound(error_message="Página não encontrada", redirect_url="/create/")

        context = {
            "couple_name": relationship_event.couple_name,
            "message": relationship_event.message,
            "images": relationship_event.files,
            "date": relationship_event.relationship_beginning_date,
            "hour": relationship_event.relationship_beginning_hour
        }

        return context

    @staticmethod
    async def mark_as_paid(db: Session, yampi_event: YampiEvent):
        if not yampi_event.event == "order.paid":
            return

        client_email = yampi_event.resource.customer.data.email

        for product in yampi_event.resource.items.data:
            if product.sku.data.sku in ["LOVSITE", "LOVSITEP"]:
                relationship_event = db.query(RelationshipEvent).filter(RelationshipEvent.email == client_email).first()
                if not relationship_event:
                    return

                relationship_event.paid = True
                db.commit()
                email_content = f"""
                    <html>
                        <body>
                            <p>Olá!</p>
                            <p>Seu site romântico está pronto! Você pode acessar aqui:</p>
                            <p><a href="https://lovesite.lovechocolate.com.br/{relationship_event.small_id}/{relationship_event.couple_slug}">
                                Clique aqui para ver seu site
                            </a></p>
                            <br/>
                            <p>Ou copie o link abaixo:</p>
                            <p>https://lovesite.lovechocolate.com.br/{relationship_event.small_id}/{relationship_event.couple_slug}</p>
                            <p>Atenciosamente,<br/>Time da Love</p>
                        </body>
                    </html>
                """
                email_title = "Seu site romântico está pronto"

                email_sender = EmailSender(AZURE_APPLICATION_ID, AZURE_CLIENT_SECRET_VALUE, AZURE_TENANT_ID)
                email_sender.send_email(to_emails=[client_email], subject=email_title, content=email_content, content_type="HTML")

            elif product.sku.data.sku in ["LOVCARDSDIG"]:
                love_cards_costumer = db.query(LoveCardsCustomer).filter(LoveCardsCustomer.email == client_email).first()
                if not love_cards_costumer:
                    new_customer = LoveCardsCustomer(
                        email=client_email,
                        cpf=yampi_event.resource.customer.data.cpf,
                        paid=True,
                        paid_at=yampi_event.resource.updated_at.date,
                        amount_paid=yampi_event.resource.buyer_value_total,
                        payment_method=yampi_event.resource.payments[0].name
                    )
                    db.add(new_customer)
                    db.commit()
                else:
                    love_cards_costumer.cpf = yampi_event.resource.customer.data.cpf
                    love_cards_costumer.paid = True
                    love_cards_costumer.paid_at = yampi_event.resource.updated_at.date
                    love_cards_costumer.amount_paid = yampi_event.resource.buyer_value_total
                    love_cards_costumer.payment_method = yampi_event.resource.payments[0].name
                    db.commit()

                email_content = """
                    <html>
                        <body>
                            <p>Olá!</p>
                            <p>Muito obrigado por comprar o Love Cards versão digital!</p>
                            <p><a href="https://love-cards-web.pages.dev/">
                                Clique aqui para acessar as cartas
                            </a></p>
                            <p>O login será feito com o CPF que você utilizou em sua compra.</p>
                            <br/>
                            <p>Ou copie o link abaixo:</p>
                            <p>https://love-cards-web.pages.dev/</p>
                            <p>Atenciosamente,<br/>Time da Love</p>
                        </body>
                    </html>
                """
                email_title = "Seu acesso ao Love Cards Digital"
                email_sender = EmailSender(AZURE_APPLICATION_ID, AZURE_CLIENT_SECRET_VALUE, AZURE_TENANT_ID)
                email_sender.send_email(to_emails=[client_email], subject=email_title, content=email_content, content_type="HTML")
