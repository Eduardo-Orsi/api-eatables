import re
import enum
import uuid

from unidecode import unidecode
from sqlalchemy import Column, String, Date, Time, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..db.database import Base
from ..utils.generate_small_id import generate_small_id


class PlanType(enum.Enum):
    SIMPLE = "simple_plan"
    ADVANCED = "advanced_plan"

class RelationshipEvent(Base):
    __tablename__ = 'relationship_events'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    small_id = Column(String(8), unique=True, nullable=False, default=generate_small_id)
    email = Column(String, nullable=False)
    couple_name = Column(String, nullable=False)
    couple_slug = Column(String, nullable=False)
    relationship_beginning_date = Column(Date, nullable=False)
    relationship_beginning_hour = Column(Time, nullable=False)
    message = Column(String, nullable=False)
    plan = Column(Enum(PlanType), nullable=False)
    paid = Column(Boolean, default=False)

    files = relationship('File', back_populates='relationship_event')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.couple_slug:
            self.couple_slug = self.generate_couple_slug()

    def generate_couple_slug(self):
        normalized_name = unidecode(self.couple_name).lower()
        slug = re.sub(r'[^a-z0-9]+', '-', normalized_name)
        return slug.strip('-')
