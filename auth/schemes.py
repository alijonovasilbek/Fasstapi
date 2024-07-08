from datetime import datetime,date
from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime




class User(BaseModel):
    first_name:str
    last_name:str
    email:str
    username:str
    password1:str
    password2:str
    birth_date:date
    is_superuser:Optional[bool]=Field(False,description="superuser flag")


class UserInDB(BaseModel):
    first_name:str
    last_name:str
    email:str
    username:str
    password:str
    birth_date:date
    registered_date:datetime
    is_superuser:bool


class UserInfo(BaseModel):
    first_name:str
    last_name:str
    email:str
    username:str
    birth_date:date
    is_superuser: Optional[bool] = Field(False, description="superuser flag")


class UserLogin(BaseModel):
    username:str
    password:str




