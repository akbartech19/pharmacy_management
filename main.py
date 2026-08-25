from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from database.models import Base, User
from database.config import engine, get_db
from database.schemes import UserData, UserUpdateData

from router.drugs import drug_router
from router.sale import check_route

Base.metadata.create_all(engine)

app = FastAPI()

app.include_router(drug_router)
app.include_router(check_route)

app.add_middleware(
    CORSMiddleware,     
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["POST", "PUT"],
    allow_headers = ["*"],

)   

@app.get("/")
def welcome():
    return {"message": "Welcome to apteka"}


@app.post("/register/")
def register_user(user_data: UserData, db=Depends(get_db)):
    try:
        user = User(**user_data.model_dump())

        db.add(user)
        db.commit()
        db.refresh(user)

        return {"success": True, "data": user}

    except Exception as error:
        return {"success": False, "message": str(error)}


@app.get("/users/")
def users_get(
    admin_id: int,
    start: int = 0,
    skip: int = 10,
    db=Depends(get_db)
):
    admin = db.query(User).filter(User.id == admin_id).first()

    if not admin or admin.role.value != "admin":
        return {"success": False, "message": "Ruxsat yo'q"}

    users = db.query(User).offset(start).limit(skip).all()

    return {"success": True, "data": users}


@app.delete("/users-delete/{account_id}")
def user_delete(account_id: int, admin_id: int, db=Depends(get_db)):
    admin = db.query(User).filter(User.id == admin_id).first()

    if not admin or admin.role.value != "admin":
        return {"success": False, "message": "Ruxsat yo'q"}

    user = db.query(User).filter(User.id == account_id).first()

    if not user:
        return {"success": False, "message": "User topilmadi"}

    db.delete(user)
    db.commit()

    return {"success": True}


@app.put("/account-update/")
def account_update(
    admin_id: int,
    user_data: UserUpdateData,
    db=Depends(get_db)
):
    admin = db.query(User).filter(User.id == admin_id).first()

    if not admin or admin.role.value != "admin":
        return {"success": False, "message": "Ruxsat yo'q"}

    user = db.query(User).filter(User.id == user_data.id).first()

    if not user:
        return {"success": False, "message": "User topilmadi"}

    for key, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return {"success": True, "data": user}

