from typing import List
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from database.config import get_db
from database.models import Check, CheckItem, User, Drug

from database.schemes import CheckReturn, ItemData, ItemsOut, SaleSummary, SalesStatistics


check_router = APIRouter(tags=["Kassa API"])

@check_router.post("/open-check/", response_model = CheckReturn)
def open_check(_cashier_id:int, db = Depends(get_db)):
    cashier = db.query(User).get(_cashier_id)

    if cashier is None or cashier.role.value != "cashier":
        raise HTTPException(status_code=401, detail = "Mumkin emas")
    
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

@check_router.post("/add-item-to-check/", response_model=ItemsOut)
def add_item(item_data: ItemData, _cashier_id: int, db=Depends(get_db)):
    cashier = db.query(User).get(_cashier_id)

    if cashier is None or cashier.role.value != "cashier":
        raise HTTPException(status_code=401,detail="Mumkin emas")

    drug = db.query(Drug).get(item_data.drug_id)

    if drug is None:
        raise HTTPException(status_code=404,detail="Dori topilmadi")

    if drug.amount < item_data.quantity:
        raise HTTPException(status_code=400,detail=f"Omborda faqat {drug.amount} ta dori bor")
    
    check = db.query(Check).get(item_data.check_id)

    if check is None:
        raise HTTPException(status_code=404,detail="Check topilmadi")

    if check.cashier_id != _cashier_id:
        raise HTTPException(status_code=403, detail="Bu check sizga tegishli emas")

    item = db.query(CheckItem).filter(CheckItem.check_id == item_data.check_id, CheckItem.drug_id == item_data.drug_id).first()

    if item is not None:
        item.quantity += item_data.quantity
    else:
        item = CheckItem(quantity=item_data.quantity, drug_id=item_data.drug_id, check_id=item_data.check_id)

        db.add(item)

    drug.amount -= item_data.quantity

    db.commit()
    db.refresh(item)

    return item

@check_router.post("/remove-item/{check_id}/{item_id}")
def remove_item(cashier_id: int, check_id: int, item_id: int,db=Depends(get_db)):
    cashier = db.query(User).get(cashier_id)

    if cashier is None or cashier.role.value != "cashier":
        raise HTTPException(status_code=401, detail="Mumkin emas")

    check = db.query(Check).get(check_id)

    if check is None or check.cashier_id != cashier_id:
        raise HTTPException(status_code=404, detail="Check topilmadi")

    item = db.query(CheckItem).get(item_id)

    if item is None:
        raise HTTPException(status_code=404,detail="Check item topilmadi")

    if item.check_id != check_id:
        raise HTTPException(status_code=400,detail="Bu item ushbu checkga tegishli emas")

    drug = db.query(Drug).get(item.drug_id)

    if drug is None:
        raise HTTPException(status_code=404,detail="Dori topilmadi")

    if item.quantity <= 1:
        drug.amount += item.quantity

        db.delete(item)
        db.commit()

        return {"message": "Item o'chirildi va dori omborga qaytarildi"}

    else:
        item.quantity -= 1
        drug.amount += 1

        db.commit()
        db.refresh(item)

        return item
    
@check_router.get("/sales/", response_model = List[SaleSummary])
def get_checks(admin_id:int, db=Depends(get_db)):
    cashier = db.query(User).get(admin_id)

    if cashier is None or cashier.role.value != "admin":
        raise HTTPException(status_code=401, detail= "Mumkin emas !")
    
    sales = db.query(Check).all()

    result = []

    for sale in sales:
        total_sales = 0
        total_profit = 0

        for item in sale.items:
            total_sales += item.quantity * item.drug.sell_price

            total_profit += item.quantity * (
                item.drug.sell_price - item.drug.base_price
            )
        
        result.append({
            "check_id": sale.id,
            "check_num": sale.check_num,
            "date_created": sale.date_created,
            "total_sales": total_sales,
            "total_profit": total_profit
        })

    return result

@check_router.get("/sales-statistics/", response_model=SalesStatistics)
def sales_statistics(admin_id: int, period: str = "day", db=Depends(get_db)):
    admin = db.query(User).get(admin_id)

    if admin is None or admin.role.value != "admin":
        raise HTTPException(status_code=401, detail="Mumkin emas!")
    
    now = datetime.now()

    if period == "day":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    elif period == "week":
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    elif period == "month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    else:
        raise HTTPException(status_code=400, detail="Period day, week yoki month bo'lishi kerak")

    sales = db.query(Check).filter(Check.date_created >= start_date).all()

    total_sales = 0
    total_profit = 0

    for sale in sales:
        for item in sale.items:
            total_sales += (item.quantity * item.drug.sell_price)

            total_profit += (item.quantity * (item.drug.sell_price - item.drug.base_price))

    return {
        "period": period,
        "total_checks": len(sales),
        "total_sales": total_sales,
        "total_profit": total_profit
    }

@check_router.get("/top-drugs/")
def top_drugs(admin_id: int, db=Depends(get_db)):
    admin = db.query(User).get(admin_id)

    if admin is None or admin.role.value != "admin":
        raise HTTPException(status_code=401,detail="Mumkin emas!")

    drugs = db.query(Drug).all()

    result = []

    for drug in drugs:
        total_quantity = 0

        for item in drug.check_items:
            total_quantity += item.quantity

        result.append({"drug_id": drug.id, "name": drug.name, "total_sold": total_quantity})

    result.sort(key=lambda x: x["total_sold"],reverse=True)

    return result

@check_router.delete("/delete-check/{check_id}")
def delete_check(check_id: int,cashier_id: int,db=Depends(get_db)):
    cashier = db.query(User).get(cashier_id)

    if cashier is None or cashier.role.value != "cashier":
        raise HTTPException(status_code=401, detail="Mumkin emas")

    check = db.query(Check).get(check_id)

    if check is None:
        raise HTTPException(status_code=404, detail="Check topilmadi")

    if check.cashier_id != cashier_id:
        raise HTTPException(status_code=403, detail="Bu check sizga tegishli emas")

    for item in check.items:
        drug = db.query(Drug).get(item.drug_id)

        if drug is not None:
            drug.amount += item.quantity

  
    db.delete(check)
    db.commit()

    return {"success": True, "message": "Check o'chirildi va dorilr omborga qaytarildi"}

