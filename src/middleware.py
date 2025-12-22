from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging

# 1. Configure the Logger
# We specificially use 'uvicorn.access' so our logs look like the standard server logs
logger = logging.getLogger("uvicorn.access")
# Ensure it's not disabled
logger.disabled = False 

async def log_request_time(request: Request, call_next):
    """
    Middleware to log the method, URL, and execution time of every request.
    """
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Calculate duration
    process_time = time.time() - start_time
    
    # Log using the standard Python logging module
    message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - completed in {process_time:.4f}s"
    logger.info(message)
    
    # Add custom header to response (visible in Postman)
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

def register_middleware(app: FastAPI):
    """
    Central function to register all middleware.
    """
    # A. Register Custom Logging
    # We use 'http' middleware for intercepting requests
    app.middleware("http")(log_request_time)
    
    # B. Register CORS (Cross-Origin Resource Sharing)
    # This allows your API to be called from a web browser on a different domain/port
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # In production, change this to ["http://localhost:3000"]
        allow_methods=["*"], # Allow GET, POST, PUT, DELETE, etc.
        allow_headers=["*"], # Allow Authorization, Content-Type, etc.
        allow_credentials=True,
    )
    
    # C. Register Trusted Hosts
    # Prevents HTTP Host Header attacks (Security best practice)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"] # Add your domain.com here later
    )