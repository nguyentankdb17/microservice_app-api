from typing import List
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status
import src.models as models
import src.schemas as schemas
from fastapi import APIRouter
from src.database import get_db

# Initialize the router
router = APIRouter(
    prefix="/api/cars",
    tags=["cars"]
)

# Define the routes for getting the cars list
@router.get("/list", response_model=List[schemas.Car])
def get_cars(db: Session = Depends(get_db)):
    cars = db.query(models.Car).all()
    return cars

# Define the routes for creating a car
@router.post("/create", response_model=schemas.Car)
def create_car(car: schemas.CreateCar, db: Session = Depends(get_db)):
    new_car = models.Car(**car.model_dump())
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

# Define the routes for updating a car
@router.put("/update/{car_id}", response_model=schemas.Car)
def update_car(car_id: int, car: schemas.Car, db: Session = Depends(get_db)):
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="car not found")
    for key, value in car.model_dump().items():
        setattr(db_car, key, value)
    db.commit()
    db.refresh(db_car)
    return db_car

# Define the routes for deleting a car
@router.delete("/delete/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(car_id: int, db: Session = Depends(get_db)):
    db_car = db.query(models.Car).filter(models.Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="car not found")
    db.delete(db_car)
    db.commit()
    return