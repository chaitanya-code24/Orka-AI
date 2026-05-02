# Orka AI

Orka AI is a lightweight LangGraph-based framework for building action-oriented AI agents in Python. It provides a clean public API, a reusable tool registry, simple service integrations, and a graph workflow that turns a natural language request into deterministic tool execution steps.

## Overview

Orka is designed as a small framework project rather than a one-off script. The current implementation focuses on:

- a package-first project structure
- a public `OrkaAgent` entry point
- LangGraph state, nodes, and workflow compilation
- optional LLM-based planning with deterministic offline fallback
- human approval gates before selected tools execute
- reusable tool registration
- config-driven tool loading
- simple in-memory service integrations

The default example flow plans and executes two actions:

1. create a customer
2. send an email

## Architecture

Orka uses a LangGraph workflow with these core stages:

1. `planner_node`
2. `tool_node`
3. `validator_node`
4. conditional routing via `decision_node`

High-level flow:

```text
User Query
  -> OrkaAgent
  -> load config
  -> build LangGraph workflow
  -> planner node, using an LLM planner when configured or the rule-based fallback
  -> tool node
  -> validator node
  -> continue / retry / end
  -> final output
```

Project layout:

```text
orka/
├── orka/
│   ├── __init__.py
│   ├── agent/
│   ├── config/
│   ├── core/
│   ├── graph/
│   ├── services/
│   └── tools/
├── examples/
├── tests/
├── config.json
├── pyproject.toml
└── README.md
```

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

For editable installation:

```bash
pip install -e .
```

## Configuration

Orka loads configuration from a JSON file.

Example `config.json`:

```json
{
  "llm": {
    "provider": "groq",
    "model": "llama-3.3-70b-versatile"
  },
  "tools": [
    "create_customer_tool",
    "send_email_tool"
  ]
}
```

Supported config behavior:

- `tools` is required
- `model` is optional
- legacy `llm` config is still accepted and mapped into the internal model config
- `approval_required_tools` is optional and can list tool names or `"*"` for all tools

## Usage

Basic example:

```python
from orka import OrkaAgent

agent = OrkaAgent("config.json")
print(agent.run("create customer Alice in Pune and send email to alice@example.com message Welcome Alice"))
```

Run the included example:

```bash
python -m examples.basic
```

Run from the CLI:

```bash
orka run "create customer Alice in Pune and send email to alice@example.com message Welcome Alice"
```

Start the API server:

```bash
orka serve --config config.json --host 127.0.0.1 --port 8000
```

Submit a run over HTTP:

```bash
curl -X POST http://127.0.0.1:8000/runs ^
  -H "Content-Type: application/json" ^
  -d "{\"query\": \"create customer Alice in Pune and send email to alice@example.com message Welcome Alice\"}"
```

Approve a waiting run:

```bash
curl -X POST http://127.0.0.1:8000/runs/{run_id}/approve
```

Example output:

```python
{
  'success': True,
  'status': 'completed',
  'output': {
    'steps': [...],
    'last_result': {
      'success': True,
      'email': {
        'to': 'alice@example.com',
        'message': 'Welcome Alice',
        'status': 'sent'
      },
      'message': 'Email sent to alice@example.com.'
    }
  },
  'steps': [...],
  'errors': [],
  'message': 'Request completed successfully.'
}
```

## Framework Components

`OrkaAgent`

- public API for loading config and running the graph
- supports `approve_run(run_id)` for human-gated workflows

`graph`

- `AgentState` typed state definition
- node functions for planning, execution, validation, and routing
- LLM and rule-based planner implementations
- `build_graph()` for compiling the LangGraph workflow

`tools`

- decorator-based registration
- global lookup by tool name

`services`

- CRM customer creation
- email sending
- simple in-memory persistence for demo flows

## Resume Notes

This project demonstrates practical LangGraph concepts including:

- state-driven workflow design
- graph node composition
- conditional routing
- tool orchestration through a reusable registry
- framework-oriented Python packaging

## Status

Current implementation is intentionally lightweight and framework-oriented. It is well suited for learning, demos, resume projects, and extension into more advanced agent workflows.
