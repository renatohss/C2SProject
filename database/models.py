from datetime import datetime
from decimal import Decimal

from sqlalchemy import Integer, String, Numeric, DateTime, func
from sqlalchemy import Enum as EnumField
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from database.enums import FuelType, TransmissionType


class Base(DeclarativeBase):
    pass


class Vehicle(Base):
    __tablename__ = 'vehicle'

    # Vehicle details
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    manufacturer: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer)
    vin: Mapped[str] = mapped_column(String(17), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    color: Mapped[str] = mapped_column(String(30))
    mileage: Mapped[int] = mapped_column(Integer)
    fuel_type: Mapped[str] = mapped_column(EnumField(FuelType), nullable=False)
    transmission: Mapped[str] = mapped_column(EnumField(TransmissionType), nullable=False)
    tank_capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    updated_by: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        return f"{self.model_name}, by {self.manufacturer} ({self.year})"