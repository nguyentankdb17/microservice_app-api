from datetime import date
from pydantic import BaseModel

class CarBase(BaseModel):
    name: str
    brand: str
    image_url: str
    price: int
    description: str
    is_available: bool

    class Config:
        from_attributes = True

class CreateCar(CarBase):
    pass

class Car(CarBase):
    id: int
