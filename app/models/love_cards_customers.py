import os
import uuid
import random
import string
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, Boolean, Float

from ..db.database import Base
from ..integration.office_365_mailer import EmailSender


AZURE_APPLICATION_ID = os.getenv("AZURE_APPLICATION_ID")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_SECRET_VALUE = os.getenv("AZURE_CLIENT_SECRET_VALUE")


def generate_otc() -> str:
    """Generate a 6-digit numeric code"""
    return ''.join(random.choices(string.digits, k=6))


def send_email_otc(code: str, client_email: str) -> None:
    email_content = f"""
        <html>
            <body>
                <p>Olá!</p>
                <p>Seu código de login do Love Cards</p>
                <p>{code}</p>
                <p>O login será feito com o CPF que você utilizou em sua compra.</p>
                <br/>
                <p>Atenciosamente,<br/>Time da Love</p>
            </body>
        </html>
    """
    email_title = f"Código de Acesso: {code} - Love Cards"
    email_sender = EmailSender(AZURE_APPLICATION_ID, AZURE_CLIENT_SECRET_VALUE, AZURE_TENANT_ID)
    email_sender.send_email(to_emails=[client_email], subject=email_title, content=email_content, content_type="HTML")


class LoveCardsCustomer(Base):
    __tablename__ = 'love_cards_customers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    cpf = Column(String, unique=True, nullable=True)
    paid = Column(Boolean, default=False)
    paid_at = Column(DateTime, nullable=True)
    amount_paid = Column(Float, nullable=True, default=0.0)
    payment_method = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class LoveCardsAuth(Base):
    __tablename__ = 'love_cards_auth'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)
