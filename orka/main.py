import logging
import os
from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from orka import OrkaAgent
from orka.core.exceptions import ConfigError, GraphExecutionError, OrkaError, ValidationError
from orka.core.logging import log_event


class RunRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language task for Orka to execute.")


class RunResponse(BaseModel):
    success: bool
    status: str
    output: dict | None = None
    steps: list[dict] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    message: str
    run_id: str
    timestamp: str


@lru_cache(maxsize=1)
def get_agent() -> OrkaAgent:
    config_path = os.getenv("ORKA_CONFIG_PATH", "config.json")
    return OrkaAgent(config_path)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Orka API",
        version="0.1.0",
        description="LangGraph-based AI action orchestration framework API.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/runs", response_model=RunResponse)
    def create_run(payload: RunRequest) -> dict[str, object]:
        log_event(logging.INFO, "api.run.create", "Received run request")
        return get_agent().run(payload.query)

    @app.get("/runs", response_model=list[RunResponse])
    def list_runs() -> list[dict[str, object]]:
        return get_agent().list_runs()

    @app.get("/runs/{run_id}", response_model=RunResponse)
    def get_run(run_id: str) -> dict[str, object]:
        run = get_agent().get_run(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail=f"Run '{run_id}' was not found.")
        return run

    @app.exception_handler(ConfigError)
    @app.exception_handler(GraphExecutionError)
    @app.exception_handler(ValidationError)
    @app.exception_handler(OrkaError)
    async def handle_orka_error(request, exc: OrkaError):  # type: ignore[override]
        status_code = 400
        if isinstance(exc, GraphExecutionError):
            status_code = 500
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    return app


app = create_app()
