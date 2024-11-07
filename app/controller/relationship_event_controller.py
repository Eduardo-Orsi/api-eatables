import os
from typing import Optional
from datetime import date, time

from fastapi import UploadFile, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import ValidationError

from ..models.file import File
from ..models.relationship_event import RelationshipEvent
from ..schema.relationship_event_schema import RelationshipEventForm
from ..schema.yampi_event import YampiEvent
from ..integration.wordpress import WordPress
from ..integration.office_365_mailer import EmailSender
from ..utils.url_helper import slugfy


WP_API_URL = os.getenv("WP_API_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

AZURE_APPLICATION_ID = os.getenv("AZURE_APPLICATION_ID")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_SECRET_VALUE = os.getenv("AZURE_CLIENT_SECRET_VALUE")


class RelationshipNotFound(Exception):
    def __init__(self, error_message: str):
        self.error_message = error_message


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
            uploaded_file = await wp_site.upload_file(file)
            file_record = File(
                relationship_event_id=relationship_event.id,
                filename=uploaded_file.title.rendered,
                content_type=uploaded_file.mime_type,
                url=uploaded_file.source_url.unicode_string(),
                wordpress_id=uploaded_file.id
            )
            db.add(file_record)
        db.commit()
        user_email = relationship_event_schema.email
        return RedirectResponse(status_code=301, url=f"https://seguro.lovechocolate.com.br/r/AMDUAUSCKJ?utm_campaign={user_email}&utm_source={user_email}")

    @staticmethod
    async def get_relationship_event(db: Session, small_id: str) -> dict:
        relationship_event = db.query(RelationshipEvent).filter(RelationshipEvent.small_id == small_id).first()
        if not relationship_event:
            raise RelationshipNotFound(error_message="Página não encontrada")

        context = {
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
            if product.sku.data.sku == "LOVSITE":
                relationship_event = db.query(RelationshipEvent).filter(RelationshipEvent.email == client_email).first()
                if not relationship_event:
                    return

                relationship_event.paid = True
                db.commit()
                print(relationship_event.small_id)
                email_content = f"""
                    Seu site personalizado: http://0.0.0.0:8000/{relationship_event.small_id}/{relationship_event.couple_slug}
                """

                email_sender = EmailSender(AZURE_APPLICATION_ID, AZURE_CLIENT_SECRET_VALUE, AZURE_TENANT_ID)
                email_sender.send_email(to_emails=[client_email], subject="Teste", content=email_content)