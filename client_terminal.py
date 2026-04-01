import asyncio
import json
import os
import re
import sys

import httpx
from dotenv import load_dotenv
from mcp import stdio_client, ClientSession, StdioServerParameters

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL_NAME = os.getenv("MODEL_NAME")


async def ask_ollama(prompt: str, is_json: bool = True):
    async with httpx.AsyncClient() as client:
        response = await client.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "format": "json" if is_json else None
        }, timeout=30.0)

        raw_content = response.json()["response"]

        if is_json:
            try:
                # Remove qualquer texto antes ou depois do JSON (Regex para pegar entre { })
                json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return json.loads(raw_content)
            except Exception as e:
                print(f"⚠️ [AI Debug]: Model returned invalid JSON: {raw_content}")
                raise e
        return raw_content


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
                    break

                # 1. MELHORIA NO PROMPT: Instruções mais rígidas para o JSON
                extraction_prompt = f"""
                ### INSTRUCTION ###
                Extract car search filters from the user input.
                Return ONLY a JSON object. No conversation. No explanations.

                ### SCHEMA ###
                {{
                  "manufacturer": "string or null",
                  "model_name": "string or null",
                  "max_value": "number or null"
                }}

                ### USER INPUT ###
                "{user_input}"

                ### JSON RESPONSE ###
                """

                try:
                    extracted_data = await ask_ollama(extraction_prompt)
                    # Atualiza apenas o que não for null
                    if isinstance(extracted_data, dict):
                        new_data = {k: v for k, v in extracted_data.items() if v is not None}
                        current_filters.update(new_data)
                except Exception as e:
                    print(f"[System Debug]: Failed to parse AI response.")

                # 2. MELHORIA NA LÓGICA: Se o usuário falou algo, tentamos buscar ou perguntar de forma variada
                # Se temos filtros ou se o usuário digitou algo específico que parece uma marca
                has_filters = any(current_filters.values())

                if has_filters:
                    print(f"[System]: Searching for {current_filters}...")

                    try:
                        result = await session.call_tool("search_vehicles", current_filters)
                        db_data = result.content[0].text

                        response_prompt = f"User asked for a car. Stock data: {db_data}. Summarize this in a friendly way."
                        friendly_text = await ask_ollama(response_prompt, is_json=False)
                        print(f"[C2S Agent]: {friendly_text}")
                    except Exception as e:
                        print(f"[C2S Agent]: I found an issue accessing the stock. Can you try again?")
                else:
                    print(
                        "[C2S Agent]: I'm sorry, I didn't quite catch that. Which car brand or price range are you interested in?")

if __name__ == "__main__":
    asyncio.run(run_local_agent())