from typing import Optional
from pydantic import BaseModel

from database.models import UserRole


class UserData(BaseModel):
    username: str
    password: str
    role: UserRole
    full_name: Optional[str] = None