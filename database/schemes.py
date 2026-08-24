from typing import Optional
from pydantic import BaseModel

from database.models import UserRole


class UserData(BaseModel):
    username: str
    password: str
    role: UserRole
    full_name: Optional[str] = None


class UserUpdateData(BaseModel):
    id: int
    username: str | None = None
    password: str | None = None
    full_name: str | None = None
    role: UserRole | None = None

class DrugData(BaseModel):
    name: str
    amount: int 
    description: str
    base_price: float
    sell_price: float

class DrugDataUpdate(BaseModel):
    id : int
    name : str| None = None
    bace_price : float| None = None 
    sell_price : float| None = None 
    description : float| None = None

class DrugEnter(BaseModel):
    id : int
    amount : int



