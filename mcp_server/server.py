import asyncio
import os
import sys
from typing import Any

from dotenv import load_dotenv
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types
from mcp.types import TextContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import structlog

from mcp_server.tools import available_tools, tools_descriptions

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
)
log = structlog.get_logger()

load_dotenv()
engine = create_engine(os.getenv("POSTGRES_URL"))
SessionLocal = sessionmaker(bind=engine)

server = Server("c2s-vehicle-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return tools_descriptions


@server.call_tool()
async def handle_call_tool(
        name: str, arguments: dict | None
) -> list[TextContent] | None | Any:
    session = SessionLocal()
    try:
        return available_tools[name](arguments, session)
    except KeyError as e:
        log.error("tool_not_found", tool=name, error=str(e))
        return [types.TextContent(type="text", text=f"Tool '{name}' is not registered in the server.")]
    except Exception as e:
        log.error("mcp_tool_error", tool=name, error=str(e))
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    finally:
        session.close()


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="c2s-vehicle-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())