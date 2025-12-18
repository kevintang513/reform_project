from fastapi import FastAPI, HTTPException, Security, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime, UTC
import logging
import os
from database import init_database, save_invoice, get_all_invoices, get_invoice_by_number, get_invoice_count

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
# Set your bearer token here or use environment variable
BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", "your-secret-token-here")
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the bearer token from the Authorization header
    """
    if credentials.credentials != BEARER_TOKEN:
        logger.warning(f"Invalid token attempt: {credentials.credentials[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Initialize FastAPI app
app = FastAPI(
    title="JSON POST Endpoint API",
    description="A simple API that accepts POST requests with JSON data (Bearer token required)",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()
    logger.info("Application started and database initialized")

# Define a Pydantic model for request validation
# This is a flexible model that accepts any JSON structure
class JSONData(BaseModel):
    data: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "age": 30
                }
            }
        }

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint - returns basic API information
    """
    return {
        "message": "JSON POST Endpoint API",
        "status": "running",
        "endpoints": {
            "POST /data": "Submit JSON data",
            "GET /docs": "Interactive API documentation",
            "GET /health": "Health check"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat()
    }

# Main POST endpoint for receiving JSON data
@app.post("/data")
async def receive_data(json_data: JSONData, token: str = Depends(verify_token)):
    """
    Receives JSON data via POST request (requires bearer token authentication)

    Args:
        json_data: JSONData model containing the data payload
        token: Bearer token from Authorization header

    Returns:
        Success message with received data and metadata
    """
    try:
        # Log the received data
        logger.info(f"Received data: {json_data.data}")

        # Process the data (you can add your custom logic here)
        response = {
            "status": "success",
            "message": "Data received successfully",
            "received_data": json_data.data,
            "timestamp": datetime.now(UTC).isoformat(),
            "data_keys": list(json_data.data.keys()) if isinstance(json_data.data, dict) else None
        }

        return response

    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Alternative endpoint that accepts any JSON structure directly
@app.post("/data/raw")
async def receive_raw_data(payload: Dict[str, Any], token: str = Depends(verify_token)):
    """
    Receives any JSON structure directly without wrapping in 'data' field (requires bearer token)

    Args:
        payload: Any valid JSON object
        token: Bearer token from Authorization header

    Returns:
        Success message with received payload
    """
    try:
        logger.info(f"Received raw data: {payload}")

        # Save to database
        record_id = save_invoice(payload)

        return {
            "status": "success",
            "message": "Raw data received successfully",
            "received_data": payload,
            "database_id": record_id,
            "timestamp": datetime.now(UTC).isoformat()
        }

    except Exception as e:
        logger.error(f"Error processing raw data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Get all invoices
@app.get("/invoices")
async def list_invoices(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    token: str = Depends(verify_token)
):
    """
    Retrieve all invoices from the database (requires authentication)

    Args:
        limit: Maximum number of records to return (1-1000)
        offset: Number of records to skip
        token: Bearer token from Authorization header

    Returns:
        List of invoices and metadata
    """
    try:
        invoices = get_all_invoices(limit=limit, offset=offset)
        total_count = get_invoice_count()

        return {
            "status": "success",
            "total_count": total_count,
            "returned_count": len(invoices),
            "limit": limit,
            "offset": offset,
            "invoices": invoices
        }

    except Exception as e:
        logger.error(f"Error retrieving invoices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Get invoice by invoice number
@app.get("/invoices/{invoice_number}")
async def get_invoice(invoice_number: str, token: str = Depends(verify_token)):
    """
    Retrieve a specific invoice by invoice number (requires authentication)

    Args:
        invoice_number: The invoice number to search for
        token: Bearer token from Authorization header

    Returns:
        Invoice data or 404 if not found
    """
    try:
        invoice = get_invoice_by_number(invoice_number)

        if not invoice:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_number} not found")

        return {
            "status": "success",
            "invoice": invoice
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
