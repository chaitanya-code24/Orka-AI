# AI Action Orchestration Agent

A production-leaning AI agent system that translates natural language into API actions using a tool-based architecture.

## Features

- FastAPI backend
- LangChain agent for tool orchestration
- Dynamic tool registry (plug-and-play)
- Validation layer for safety
- Memory layer for context
- Logging & observability
- Multi-step task execution (planner)

## Architecture

User Input ? Agent (LLM) ? Tool Selection ? API Execution ? Response

## Setup

1. Clone the repository
2. Create a virtual environment: python -m venv .venv
3. Activate the environment: .venv\Scripts\activate
4. Install dependencies: pip install -r requirements.txt
5. Copy .env.example to .env and add your Groq API key
6. Run the application: python run.py

## Usage

Send a POST request to /agent/execute with JSON:

{
  "query": "Add 5 and 3",
  "context": {}
}

## API Documentation

Visit http://localhost:8000/docs for interactive API docs.
