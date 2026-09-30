from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)

class UserOut(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    is_admin: bool

    model_config = {'from_attributes': True}

class LoginIn(BaseModel):
    email: str
    password: str

class AccessTokenOut(BaseModel):
    access_token: str
    token_type: str = 'bearer'