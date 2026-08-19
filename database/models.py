from sqlalchemy.orm import relationship
from enum import Enum as PyEnumClass
from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, Enum, DateTime

from database.config import Base


class UserRole(PyEnumClass):
    ADMIN = "admin"
    CASHIER = "cashier"


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String(50), nullable=True)
    role = Column(Enum(UserRole), nullable=False)

    checks = relationship("Check", back_populates="cashier")


class Drug(Base):
    __tablename__ = "drug"

    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    amount = Column(Integer, default=0)
    description = Column(Text, nullable=False)
    base_price = Column(Float, default=0)
    sell_price = Column(Float, default=0)
    bar_code = Column(String(20))

    check_items = relationship("CheckItem", back_populates="drug")


class Check(Base):
    __tablename__ = "checks"

    id = Column(Integer, primary_key=True)
    check_num = Column(String, unique=True)
    date_created = Column(DateTime, nullable=False)

    cashier_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    cashier = relationship("User", back_populates="checks")
    items = relationship("CheckItem", back_populates="check")


class CheckItem(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    amount = Column(Integer, default=0)

    drug_id = Column(Integer, ForeignKey("drug.id"), nullable=False)
    drug = relationship("Drug", back_populates="check_items")

    check_id = Column(Integer, ForeignKey("checks.id"), nullable=False)
    check = relationship("Check", back_populates="items")