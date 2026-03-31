from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from database.enums import TransmissionType, FuelType

class VINSearch(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vin: str = Field(None, alias="vin", description="VIN of the vehicle")


class VehicleSearchFilters(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    manufacturer: Optional[str] = Field(None, alias="manufacturer", description="Manufacturer of the vehicle")
    model_name: Optional[str] = Field(None, alias="model_name", description="Model of the vehicle")
    year: Optional[int] = Field(None, alias="year", description="Year of the vehicle")
    min_value: Optional[int] = Field(None, alias="min_value", description="Minimum value of the vehicle")
    max_value: Optional[int] = Field(None, alias="max_value", description="Maximum value of the vehicle")
    color: Optional[str] = Field(None, alias="color", description="Color of the vehicle")
    min_mileage: Optional[int] = Field(None, alias="mileage", description="Minimum mileage of the vehicle")
    max_mileage: Optional[int] = Field(None, alias="mileage", description="Maximum mileage of the vehicle")
    fuel_type: Optional[FuelType] = Field(None, alias="fuel_type", description="Fuel type of the vehicle")
    transmission: Optional[TransmissionType] = Field(None, alias="transmission", description="Transmission of the vehicle")
    tank_capacity: Optional[int] = Field(None, alias="tank_capacity", description="Capacity of the vehicle")
