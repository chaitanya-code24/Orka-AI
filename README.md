# 🧠 Orka AI — Action-Oriented Agent Framework

<p align="center">
  <b>A lightweight LangGraph-based framework for building deterministic, tool-driven AI agents.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-active-success.svg" />
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" />
  <img src="https://img.shields.io/badge/license-MIT-green.svg" />
</p>

---

## 📌 Overview

**Orka AI** is a lightweight, modular framework for building **action-oriented AI agents** in Python.

Unlike typical LLM wrappers, Orka focuses on:

* deterministic execution
* structured workflows
* real tool integration

It converts natural language queries into **controlled, step-by-step tool execution pipelines**.

---

## 🚀 Key Highlights

* 🧩 **LangGraph-powered workflows**
* 🧠 **LLM planning with rule-based fallback**
* 🛠 **Reusable tool registry with schema discovery**
* 🔐 **Human approval gates for safe execution**
* ⚙️ **Config-driven architecture**
* 🔌 **Multi-service connectors (Gmail, Slack, Notion, etc.)**
* 📦 **Package-first project structure**

---

## ⚙️ Architecture

Orka uses a structured LangGraph pipeline:

```text
User Query
   │
   ▼
OrkaAgent
   │
   ▼
Planner Node (LLM / Rule-based)
   │
   ▼
Tool Node
   │
   ▼
Validator Node
   │
   ▼
Decision Node (continue / retry / end)
   │
   ▼
Final Output
```

---

## 🏗 Project Structure

```text
orka/
├── orka/
│   ├── agent/        # Agent entrypoint
│   ├── config/       # Configuration handling
│   ├── core/         # Core utilities
│   ├── graph/        # LangGraph workflow logic
│   ├── services/     # Service integrations
│   └── tools/        # Tool registry and implementations
├── examples/
├── tests/
├── config.json
├── pyproject.toml
└── README.md
```

---

## 🧠 Execution Flow Example

Default example:

1. Create a customer
2. Send an email

```text
Input:
"create customer Alice in Pune and send email to alice@example.com message Welcome Alice"

Execution:
→ plan steps  
→ execute tools  
→ validate output  
→ return result  
```

---

## ⚙️ Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

For development mode:

```bash
pip install -e .
```

---

## 🔧 Configuration

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

### Notes:

* `tools` → required
* `model` → optional
* supports legacy LLM config
* optional `approval_required_tools`

---

## 🧪 Usage

### Python API

```python
from orka import OrkaAgent

agent = OrkaAgent("config.json")
print(agent.run("create customer Alice in Pune and send email to alice@example.com message Welcome Alice"))
```

---

### CLI

```bash
orka run "create customer Alice in Pune and send email to alice@example.com message Welcome Alice"
```

---

### Start API Server

```bash
orka serve --config config.json --host 127.0.0.1 --port 8000
```

Dashboard:

```
http://127.0.0.1:8000/dashboard
```

---

### HTTP Request

```bash
curl -X POST http://127.0.0.1:8000/runs ^
  -H "Content-Type: application/json" ^
  -d "{\"query\": \"create customer Alice in Pune and send email to alice@example.com message Welcome Alice\"}"
```

---

### Approve Run

```bash
curl -X POST http://127.0.0.1:8000/runs/{run_id}/approve
```

---

## 📊 Example Output

```python
{
  "success": true,
  "status": "completed",
  "output": {
    "steps": [...],
    "last_result": {
      "success": true,
      "email": {
        "to": "alice@example.com",
        "message": "Welcome Alice",
        "status": "sent"
      }
    }
  }
}
```

---

## 🧩 Framework Components

### 🔹 OrkaAgent

* Main public API
* Loads config and executes workflows
* Supports human approval flows

### 🔹 Graph System

* Typed `AgentState`
* Planner, tool, validator, decision nodes
* Workflow compilation via LangGraph

### 🔹 Tool System

* Decorator-based registration
* Schema-driven tool contracts
* Global registry lookup

List tools:

```bash
curl http://127.0.0.1:8000/tools
```

---

## 🔌 Connectors

Available integrations:

* Gmail
* Google Sheets
* Notion
* HubSpot
* Slack

Modes:

* `demo` (default)
* `live` via environment variables

---

## 🐳 Docker

```bash
docker compose up --build
```

API:

```
http://127.0.0.1:8000
```

Dashboard:

```
http://127.0.0.1:8000/dashboard
```

---

## 🎯 What This Project Demonstrates

* State-driven agent workflows
* Graph-based orchestration
* Tool abstraction layers
* Config-driven design
* Real-world integration patterns

---

## 📌 Status

Orka AI is intentionally lightweight and designed for:

* learning
* prototyping
* extending into advanced agent systems

---

## 📄 License

MIT License

---

## 🙌 Contributing

Contributions are welcome.
Feel free to open issues or submit pull requests.

---
