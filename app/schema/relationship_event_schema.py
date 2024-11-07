from enum import Enum
from datetime import date, time

from pydantic import BaseModel, Field, EmailStr


class PlanType(Enum):
    SIMPLE = "simple_plan"
    ADVANCED = "advanced_plan"


class RelationshipEventForm(BaseModel):
    email: EmailStr = Field(..., description="E-mail do cliente")
    couple_name: str = Field(..., description="Nome do casal", max_length=150, min_length=3)
    relationship_beginning_date: date
    relationship_beginning_hour: time
    message: str = Field(..., description="Mensagem surpresa para o mozão")
    plan: PlanType = Field(..., description="Tipo de plano escolhido, 'simple_plan' ou 'advanced_plan'")
    paid: bool = Field(default=False, description="O cliente pagou o site ou não")
