# C2S Agent - AI Car Consultant (MCP)

This project is an intelligent vehicle sales assistant that utilizes the **MCP (Model Context Protocol)** architecture to connect a local LLM (**Ollama**) to a stock database via **PostgreSQL**.

The agent is designed to extract user search intent (manufacturer, model, and price) and query the database in real-time to provide personalized recommendations.

---

## Technical Stack

* **Language:** Python 3.10+
* **Local LLM:** Ollama (Llama 3.2 3B)
* **Database:** PostgreSQL (Dockerized)
* **ORM:** SQLAlchemy
* **Protocol:** MCP (Model Context Protocol) for Agent-Tool integration.

---

## Prerequisites

Before starting, ensure you have the following installed on your machine:

1.  **Docker & Docker Compose**
2.  **Python 3.10 or higher**
3.  **Ollama**

---

## Installation Guide

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd C2SProject
```

### 2. Prepare the Python Environment
It is recommended to use a virtual environment to isolate dependencies:

#### Create a new virtual environment:
```bash
python -m venv venv
```

#### Activate your virtual environment:
```bash
source venv/bin/activate
```

#### Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configure Infrastructure (Docker)
Start the PostgreSQL database container using the file in the root directory:

```bash
docker-compose up -d
```
This will create the database as configured in your docker-compose.yml.




### 4. Prepare the Database
Once the docker is up, run the alembic migration to create the table

```bash
alembic upgrade head
```

Then, run the script *db_population.py* to populate your database
```bash
cd scripts
python3 -m scripts.db_population
```
### 5. Configure the AI Model (Ollama)

Ensure Ollama is running and download the specific model:

```bash
ollama pull llama3.2:3b
```

### 6. Environment Variables
Ensure your .env file in the root directory.

## Execution

Once the database is running and the environment is configured, start the agent via the terminal:

```bash
python client_terminal.py
```

### Usage Example
* **User:** "I am looking for a Ford"
* **System:** *Extracting filters: {'manufacturer': 'Ford'}*
* **C2S Agent:** "I found some Ford models for you, such as the EcoSport and the Ka..."

---

## Project Structure

* `server.py`: MCP Server that exposes the database search tool.
* `client_terminal.py`: Chat interface and Agent orchestration logic.
* `models.py`: SQLAlchemy table definitions.
* `docker-compose.yml`: PostgreSQL container orchestration.
* `requirements.txt`: List of Python dependencies.

---

## Troubleshooting

* **DB Connection Error:** Ensure the Docker container state is **Up**. Use `docker ps` to verify.
* **Invalid JSON in Response:** The code includes a Regex cleaning layer to handle Ollama's conversational output, but if errors persist, check the status of the Ollama service.
* **Performance:** Running local LLMs depends on your CPU/GPU resources. If the model takes longer than 30s, the `timeout` in the code may require adjustment.