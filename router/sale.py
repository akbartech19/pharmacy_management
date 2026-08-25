from typing import List
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from database.config import get_db
from database.models import Check, CheckItem, Drug, User

from database.schemes import CheckReturn, ItemData, ItemsOut


check_route = APIRouter(tags=["Kassa API"])

@check_route.post("/open-check/", response_model = CheckReturn)
def open_check(_cashier_id:int, db = Depends(get_db)):
    cashier = db.query(User).get(_cashier_id)

    if cashier is None or cashier.role.value != "cashier":
        raise HTTPException(status_code=401, detil = "Mumkin emas")
    
    date = datetime.now()
    check = Check(
        check_num = f"Check- {date}",
        date_created= date,
        cashier_id = _cashier_id
    )

    db.add(check)
    db.commit()
    db.refresh(check)

    return check

@check_route.post("/add-item-to-check/", response_model = ItemsOut)
def add_item(item_data:ItemData, _cashier_id:int, db = Depends(get_db)):
    cashier = db.query(User).get(_cashier_id)       

    if cashier is None or cashier.role.value != "cashier":
        raise HTTPException(status_code=401, detail="Mumkin emas")
    
    
    item = db.query(CheckItem).filter(CheckItem.check_id == item_data.check_id).filter(CheckItem.drug_id == item_data.drug_id).first()
    if item is not None :
        item.amount += item_data.amount
        db.commit()
    else:
        item = CheckItem(amount=item_data.amount, drug_id=item_data, check_id=item_data.check_id)

        db.add(item)
        db.commit()

    db.refresh(item)
    return item


@check_route.post("/remove-item/{check_id}/{item_id}")
def remove_item(cashier_:int, check_id:int, item_id:int, db = Depends(get_db)):
    cashier=db.query(User).get(cashier_)

    if cashier is None or cashier.role.value != "cashier":
        raise HTTPException(status_code=401, detail="Mumkin emas")

    check = db.query(Check).get(check_id)
    item = db.query(CheckItem).get(item_id)

    if check is None or check.cashier_id != cashier_:
        raise HTTPException(status_code=404, detail="check topilmadi")

    if item is None:
        raise HTTPException(status_code=404, detail= "check item topilmadi")
    
    if item.amount <= 1:
        db.delete(item)
        db.commit()
        return {"message": "Item Deleted"}
    else:
        item.amount -= 1
        db.commit()
        db.refresh(item)

    return item

@check_route.get("/sales/", response_model = List[CheckReturn])
def get_checks(admin_id:int, db=Depends(get_db)):
    cashier = db.query(User).get(admin_id)

    if cashier is None or cashier.role.value != "admin":
        raise HTTPException(status_code=401, detail= "Mumkin emas !")
    
    sales = db.query(Check).all()

    return sales
