from enum import Enum

class FuelType(str, Enum):
    FLEX = "Flex"
    GASOLINE = "Gasoline"
    ALCOHOL = "Alcohol"
    DIESEL = "Diesel"
    ELECTRIC = "Electric"
    HYBRID = "Hybrid"

class TransmissionType(str, Enum):
    MANUAL = "Manual"
    AUTOMATIC = "Automatic"