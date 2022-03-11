from typing import Optional
from pydantic import BaseModel, EmailStr


class Feedback(BaseModel):
    uuid: str
    qualification: bool = False


class Category(BaseModel):
    business: str


class Business(BaseModel):
    business: str


class Log(BaseModel):
    business: str
    date_start: str
    date_end: str


class Question_Answer(BaseModel):
    business: str
    date_start: str
    date_end: str
    limit: int
    qualification: Optional[bool] = True


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None


class Msg(BaseModel):
    msg: str


class CustomerBase(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    is_active: Optional[bool] = True


class CustomerCreate(CustomerBase):
    name: str
    code: str


class CustomerUpdate(CustomerBase):
    pass


class CustomerInDBBase(CustomerBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Customer(CustomerInDBBase):
    pass


class DatasetBase(BaseModel):
    file: str
    customer_code: str
