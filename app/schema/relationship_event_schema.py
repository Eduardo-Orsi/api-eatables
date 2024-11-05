from datetime import date, time

from pydantic import BaseModel, Field


class RelationshipEventForm(BaseModel):
    couple_name: str = Field(..., description="Nome do casal", max_length=255, min_length=3)
    relationship_beginning_date: date
    relationship_beginning_hour: time
    message: str = Field(..., description="Mensagem surpresa para o mozão", max_length=255)
