import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, DateTime, Boolean

from ..db.database import Base


class SyncedOrder(Base):
    __tablename__ = 'synced_orders'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    synced = Column(Boolean, default=False ,nullable=False)
    bling_order_id = Column(Integer, unique=True, nullable=False)
    yampi_id = Column(String, nullable=False)
    shopify_order_id = Column(String, nullable=False)
    tracking_code = Column(String, nullable=False)
    tracking_campany = Column(String, nullable=False)
    tracking_url = Column(String, nullable=False)
    synced_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
