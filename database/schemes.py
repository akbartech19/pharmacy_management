from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from database.models import UserRole

class UserData(BaseModel):
    username: str
    password: str
    role: UserRole
    full_name: Optional[str] = None

class UserUpdateData(BaseModel):
    id :int
    username: str | None = None 
    password: str | None = None 
    full_name: str | None = None 
    role : UserRole | None = None 

class UserOut(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    role: UserRole


class DrugDataUpdate(BaseModel):
    id: int
    name: str | None = None
    amount: int | None = None
    base_price: float | None = None
    sell_price: float | None = None
    description: str | None = None

class DrugData(BaseModel):
    name: str
    amount: int 
    description: str
    base_price: float
    sell_price: float


class DrugEnter(BaseModel):
    drug_id : int
    quantity : int

class DrugOut(DrugData):
    id : int

class CheckData(BaseModel):
    cashier_id: int

class ItemData(BaseModel):
    drug_id: int
    check_id : int
    quantity: int

class ItemsOut(BaseModel):
    id : int
    quantity: int
    drug :DrugOut

class CheckReturn(BaseModel):
    id : int
    check_num : str
    date_created: datetime
    cashier: UserOut
    items : List[ItemsOut]= []


