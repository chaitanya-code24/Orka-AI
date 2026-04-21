import time
import json
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from core.logging import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time:.3f}s")
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Error in {request.method} {request.url.path} - Duration: {process_time:.3f}s - Error: {str(e)}")
            raise

app = FastAPI()
app.add_middleware(LoggingMiddleware)

@app.get("/health")
def health():
    logger.info("Health check endpoint called")
    return {"status": "ok"}
