import asyncio
import json
import os
import re
import sys

import httpx
import structlog
from dotenv import load_dotenv
from mcp import stdio_client, ClientSession, StdioServerParameters


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
OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME")


async def ask_ollama(prompt: str, is_json: bool = True):
    async with httpx.AsyncClient() as client:
        response = await client.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "format": "json" if is_json else None
        }, timeout=30.0)
        raw_response = response.json().get("response", "")

        if is_json:
            try:
                match = re.search(r"(\{.*\})", raw_response, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    return json.loads(json_str)
                return json.loads(raw_response)
            except Exception as e:
                log.error("ollama_error", error=str(e))
                print(f"[AI Debug] Ollama returned invalid JSON. Raw output: {raw_response}")
                raise e
        return raw_response


async def run_local_agent():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.server"],
        env=os.environ.copy()
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("[C2S Agent]: Hello! I'm your AI consultant. What are you looking for?")
            current_filters = {}

            while True:
                user_input = input("You: ")
                if user_input.lower() in ["exit", "quit", "sair"]:
                    print("[C2S Agent]: Goodbye!")
                    break

                if user_input.lower() in ["reset", "clear"]:
                    print("[C2S Agent]: Clearing search filters.")
                    current_filters = {}

                extraction_prompt = f"""
                ### INSTRUCTION ###
                Extract car search filters from the user input.
                User may ask for the total quantity of cars you have in stock, return the according value.
                Return ONLY a JSON object. No conversation. No explanations.

                ### SCHEMA ###
                {{
                  "manufacturer": "string or null",
                  "model_name": "string or null",
                  "max_value": "number or null"
                  "min_value": "number or null",
                  "fuel_type": "string or null",
                  "color": "string or null",
                  "transmission": "string or null",
                  "max_mileage": "number or null",
                  "min_mileage": "number or null",
                }}

                ### USER INPUT ###
                "{user_input}"

                ### JSON RESPONSE ###
                """

                try:
                    extracted_data = await ask_ollama(extraction_prompt)
                    if isinstance(extracted_data, dict):
                        new_data = {k: v for k, v in extracted_data.items() if v is not None}
                        current_filters.update(new_data)
                except Exception as e:
                    log.error("error_extracting_data", error=str(e))
                    print(f"[System Debug]: Failed to parse AI response.")

                clean_filters = {
                    k: v for k, v in current_filters.items()
                    if v is not None and str(v).lower() != "null"
                }

                if clean_filters:
                    print(f"[System]: Searching for {clean_filters}...")
                    try:
                        result = await session.call_tool("search_vehicles", current_filters)
                        db_data = result.content[0].text

                        response_prompt = (f"You are a car sales consultant. Use the data provided by the "
                                           f"search tool to recommend specific vehicles to the user. Do not explain "
                                           f"code or functions. Respond naturally in a conversational tone."
                                           f"User asked for a car or for the total quantity fo cars in stock."
                                           f" Stock data: {db_data}. "
                                           f"Summarize the cars above in a friendly way:" 
                                           f"Use a bulleted list. If you need more information about the car, focus"
                                           f"on manufacturer or model name." 
                                           f"If an error has occured, please ask the user politely for "
                                           f"more information")
                        friendly_text = await ask_ollama(response_prompt, is_json=False)
                        print(f"[C2S Agent]: {friendly_text}")
                    except Exception as e:
                        log.error("error_calling_mcp", error=str(e))
                        print(f"[C2S Agent]: I found an issue accessing the stock. Can you try again?")
                else:
                    print(
                        "[C2S Agent]: I'm sorry, I didn't quite catch that. Which car brand or price range "
                        "are you interested in?")

if __name__ == "__main__":
    asyncio.run(run_local_agent())