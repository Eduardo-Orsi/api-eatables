from pydantic import BaseModel, EmailStr


class EmailRegsiter(BaseModel):
    email: EmailStr
