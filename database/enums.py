from enum import Enum

class FuelType(str, Enum):
    FLEX = "flex"
    GASOLINE = "gasoline"
    ALCOHOL = "alcohol"
    DIESEL = "diesel"
    ELECTRIC = "electric"

class TransmissionType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"