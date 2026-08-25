from typing import Optional, Text, List
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

class UserOut(UserData):
    id : int

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

class DrugDataUpdate(BaseModel):
    id : int
    name : str| None = None
    bace_price : float| None = None 
    sell_price : float| None = None 
    description : str| None = None

class DrugEnter(BaseModel):
    id : int
    amount : int

class DrugOut(DrugData):
    id : int

class CheckData(BaseModel):
    cassir_id: int

class ItemData(BaseModel):
    drug_id: int
    check_id : int
    amount: int

class ItemsOut(BaseModel):
    id : int
    amount: int
    drug :DrugOut

class CheckReturn(BaseModel):
    id : int
    check_num : str
    date_created: datetime
    cashier: UserOut
    items : List[ItemsOut]= []


