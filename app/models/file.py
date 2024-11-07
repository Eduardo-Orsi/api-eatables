from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, UUID

from ..db.database import Base


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    relationship_event_id = Column(UUID(as_uuid=True), ForeignKey('relationship_events.id'), nullable=False)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    wordpress_id = Column(Integer, nullable=False)

    relationship_event = relationship('RelationshipEvent', back_populates='files')
