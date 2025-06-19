from src.database import Base
from sqlalchemy import Column, Integer, String, Boolean

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    is_available = Column(Boolean, nullable=False)