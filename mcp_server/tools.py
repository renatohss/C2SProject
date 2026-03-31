from typing import Callable, Any

import structlog
import mcp.types as types
from mcp.types import TextContent
from sqlalchemy import select, Select
from sqlalchemy.orm import Session

from database.models import Vehicle
from mcp_server.enums import Tools
from mcp_server.schemas import VehicleSearchFilters, VINSearch

log = structlog.get_logger()

def _format_vehicle_response_list(payload: Any) -> list[TextContent]:
    vehicles_data = [
        (f"Manufacturer: {v.manufacturer} | "
         f"Model: {v.model_name} | "
         f"Year: {v.year} | "
         f"VIN: {v.vin} | "
         f"Value: ${v.value} | "
         f"Color: {v.color} | "
         f"Mileage: {v.mileage} | "
         f"Fuel Type: {v.fuel_type} | "
         f"Transmission: {v.transmission} | "
         f"Tank Capacity: {v.tank_capacity}")
        for v in payload
    ]
    return [types.TextContent(type="text", text="\n".join(vehicles_data))]


def _build_search_query(filters: VehicleSearchFilters) -> Select[Any]:
    query = select(Vehicle)

    if filters.manufacturer:
        query = query.where(Vehicle.manufacturer.ilike(f"{filters.manufacturer}"))
    if filters.model_name:
        query = query.where(Vehicle.model_name.ilike(f"{filters.model_name}"))
    if filters.year:
        query = query.where(Vehicle.year == filters.year)
    if filters.min_value:
        query = query.where(Vehicle.value >= filters.min_value)
    if filters.max_value:
        query = query.where(Vehicle.value <= filters.max_value)
    if filters.color:
        query = query.where(Vehicle.color == filters.color)
    if filters.min_mileage:
        query = query.where(Vehicle.mileage >= filters.min_mileage)
    if filters.max_mileage:
        query = query.where(Vehicle.mileage <= filters.max_mileage)
    if filters.fuel_type:
        query = query.where(Vehicle.fuel_type == filters.fuel_type)
    if filters.transmission:
        query = query.where(Vehicle.transmission == filters.transmission)

    return query


def list_vehicles(arguments: dict, session: Session) -> list:
    limit = arguments.get("limit", 10)
    result = session.execute(select(Vehicle).limit(limit)).scalars().all()

    log.info("mcp_tool_called", tool=Tools.LIST_VEHICLES, count=len(result))
    return _format_vehicle_response_list(result)


def get_vehicle_by_vin(arguments: str, session: Session) -> list[TextContent]:
    search_filter = VINSearch.model_validate(arguments)
    vehicle = session.execute(select(Vehicle).where(Vehicle.vin == search_filter.vin)).scalar_one_or_none()

    if not vehicle:
        return [types.TextContent(type="text", text="Vehicle not found.")]

    log.info("mcp_tool_called", tool=Tools.GET_VEHICLE_BY_VIN)
    return _format_vehicle_response_list([vehicle])


def search_vehicles(arguments: dict, session: Session) -> list[TextContent]:
    search_filters = VehicleSearchFilters.model_validate(arguments)
    query = _build_search_query(search_filters)
    result = session.execute(query).scalars().all()
    if not result:
        return [types.TextContent(type="text", text="No vehicles found with given filters.")]

    log.info("mcp_tool_called", tool=Tools.SEARCH_VEHICLES, count=len(result))
    return _format_vehicle_response_list(result)



available_tools: dict[str, Callable] = {
    "list_vehicles": list_vehicles,
    "get_vehicle_by_vin": get_vehicle_by_vin,
    "search_vehicles": search_vehicles,
}

tools_descriptions: list[types.Tool] =[
        types.Tool(
            name="list_vehicles",
            description="Returns all vehicles available.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10},
                },
            },
        ),
        types.Tool(
            name="get_vehicle_by_vin",
            description="Search vehicle by VIN.",
            inputSchema=VINSearch.model_json_schema()
        ),
        types.Tool(
            name="search_vehicles",
            description="Search vehicles by filter params.",
            inputSchema=VehicleSearchFilters.model_json_schema()
        )
    ]