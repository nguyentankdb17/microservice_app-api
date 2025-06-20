from typing import List
from fastapi import HTTPException, Depends, Request
from sqlalchemy.orm import Session
from starlette import status
import src.models as models
import src.schemas as schemas
from fastapi import APIRouter
from src.database import get_db
from src.core.auth import verify_token, require_admin

# Initialize the router
router = APIRouter(prefix="/api/cars", tags=["cars"])


@router.get("/list", response_model=List[schemas.Car])
async def get_cars(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=403, detail="Authorization header missing"
        )

    token = auth_header.replace("Bearer ", "")
    await verify_token(token)

    cars = db.query(models.Car).all()
    return cars


# Define the routes for creating a car
@router.post("/create", response_model=schemas.Car)
async def create_car(
    car: schemas.CreateCar,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
):
    new_car = models.Car(**car.model_dump())
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car


# Define the routes for updating a car
@router.put("/update/{car_id}", response_model=schemas.Car)
async def update_car(
    car_id: int,
    car: schemas.Car,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
):
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not db_car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="car not found"
        )
    for key, value in car.model_dump().items():
        setattr(db_car, key, value)
    db.commit()
    db.refresh(db_car)
    return db_car


# Define the routes for deleting a car
@router.delete("/delete/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(
    request: Request,
    car_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
):
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not db_car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="car not found"
        )
    db.delete(db_car)
    db.commit()
    return
