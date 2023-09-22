from pydantic import BaseModel

class MenuItemIn(BaseModel):
    name: str
    description: str
    price: float

class MenuItemDb(MenuItemIn):
    id: str

class UserIn(BaseModel):
    username: str
    email: str
    password: str

class UserDb(BaseModel):
    username: str
    email: str
    hashed_password: str
