import os
import random
from decimal import Decimal

import structlog

from faker import Faker
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.enums import FuelType, TransmissionType
from database.models import Vehicle

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

load_dotenv()

db_url = os.getenv("POSTGRES_URL")
if not db_url:
    raise ValueError("Please provide a Postgres URL")

engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
fake = Faker(['en_US'])

def populate_db(count=100):
    log = logger.bind(operation="populate_vehicle_table", total_expected=count)
    try:
        session = Session()

        log.info(f"Populating Vehicle Table with {count} records")

        manufacturers_models = {
            "Toyota": ["Corolla", "Hilux", "Yaris", "SW4"],
            "Volkswagen": ["Gol", "Polo", "Nivus", "T-Cross"],
            "Honda": ["Civic", "HR-V", "City", "Fit"],
            "Ford": ["Territory", "Ranger", "Maverick"],
            "Chevrolet": ["Onix", "Tracker", "S10", "Cruze"]
        }

        vehicles_list = []
        for _ in range(count):
            manufacturer = random.choice(list(manufacturers_models.keys()))
            model_name = random.choice(manufacturers_models[manufacturer])
            user = fake.user_name()

            vehicle = Vehicle(
                manufacturer=manufacturer,
                model_name=model_name,
                year=int(fake.year()),
                vin=fake.unique.bothify(text='?#??###?#??######').upper(),
                mileage=fake.random_int(1, 100000),
                value=Decimal(random.randint(40000, 250000)) + Decimal("0.90"),
                color=fake.color_name(),
                fuel_type=random.choice(list(FuelType)),
                transmission=random.choice(list(TransmissionType)),
                tank_capacity=fake.random_int(50, 100),
                created_by=user,
                updated_by=user,
            )

            vehicles_list.append(vehicle)

        session.add_all(vehicles_list)
        session.commit()
        log.info("Vehicle Table populated successfully")

    except Exception as err:
        log.error(f"Failed to populate Vehicle table. Error: {err}")

if __name__ == "__main__":
    populate_db()