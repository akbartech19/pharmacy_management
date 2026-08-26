from fastapi import APIRouter, Depends, HTTPException
from database.config import get_db
from database.models import Drug, User
from database.schemes import DrugData, DrugDataUpdate, DrugEnter

drug_router = APIRouter(tags=["Drug routerlari"])

@drug_router.post("/drug-create/")
def drug_create(drug_data: DrugData, admin_id: int, db = Depends(get_db)):
    admin_user = db.query(User).filter(User.id == admin_id).first()
    
    if admin_user is None:
        return {"success": False, "message": "Ruxsat yo'q"}
    
    if admin_user.role.value == "admin":
        new_drug = Drug(**drug_data.model_dump())
        db.add(new_drug)
        db.commit()

        new_drug.bar_code = f"{new_drug.id} - {new_drug.name}"
        db.commit()
        db.refresh(new_drug)

        return {"message":"create !", "success":True, "data": new_drug}
    else:
        return {"message": "bir aylanib keling", "success": False}
        
@drug_router.get("/drug/{drug_id}")
def drug_get(drug_id:int,user_id:int, db = Depends(get_db)):
    user = db.query(User).get(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    
    drug = db.query(Drug).get(drug_id)

    if drug is None:
        raise HTTPException(status_code=404, detail="Not found!")

    return {"message": "Worked", "success":True, "data":drug}

@drug_router.put("/drug-update/")
def drug_update(drug_data:DrugDataUpdate, admin_id:int, db = Depends(get_db)):
    admin_user = db.query(User).get(admin_id)
    
    if admin_user is None or admin_user.role.value != "admin":
        raise HTTPException(status_code=401, detail="unauthorized access !")
    
    drug = db.query(Drug).get(drug_data.id)

    if drug is None:
        raise HTTPException(status_code=404, detail = "Drug not found ! ") 

    new_data = drug_data.model_dump(exclude_unset=True, exclude={"id"})            
    
    for key, value in new_data.items():
        setattr(drug, key, value)

    db.commit()
    db.refresh(drug)

    return {"message": "Umpdate", "success": True,  "data": drug}

@drug_router.get("/drugs/")
def drug_fetch(user_id:int, db = Depends(get_db)):
    user = db.query(User).get(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="unauthorized access !")
        
    drugs = db.query(Drug).all()

    return {"message": "Derugs list!", "success": True, "data": drugs}


@drug_router.post("/drug-amount-update/")
def drug_amount_update(drug_amount_update:DrugEnter, admin_id:int, db = Depends(get_db)):
    admin_user = db.query(User).get(admin_id)

    if admin_user is None or admin_user.role.value != "admin":
        raise HTTPException(status_code=401, detail = "unauthorized access !")
    
    drug = db.query(Drug).get(drug_amount_update.drug_id)
    if drug is None:
        raise HTTPException(status_code=404, detail="Drug is not found with this id !")
    
    drug.amount += drug_amount_update.quantity
    db.commit()
    db.refresh(drug)

    return {"message": "Amount updated ! ", "success": True, "data":drug }


@drug_router.get("/low/")
def low_amount_drug(number:int, admin_id:int, db = Depends(get_db)):
    admin_user = db.query(User).get(admin_id)

    if admin_user is None or admin_user.role.value != "admin":
        raise HTTPException(status_code=401, detail=("unauthorized access !"))
    
    drugs = db.query(Drug).filter(Drug.amount <= number).all()

    return {"message": "Filtered !", "success": True, "data":drugs}


@drug_router.delete("/drug_delete/")
def drug_delete(drug_id:int, admin_id:int, db = Depends(get_db)):
    admin_user = db.query(User).get(admin_id)

    if admin_user is None or admin_user.role.value != "admin":
        raise HTTPException(status_code=401, detail= "unauthorized access !")
    
    drug= db.query(Drug).get(drug_id)
    if drug is None:
        raise HTTPException(status_code=404, detail="drug is not found with this id")
    
    db.delete(drug)
    db.commit()
    return {"message": "deleted", "success": True}

