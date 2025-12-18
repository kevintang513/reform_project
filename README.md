# JSON POST Endpoint API

A FastAPI-based HTTP server that accepts POST requests with JSON data and can be exposed to the internet via ngrok.

## Features

- FastAPI server with automatic API documentation
- Bearer token authentication for secure access
- POST endpoints for receiving JSON data
- SQLite database for storing invoice data
- Request validation using Pydantic
- Health check endpoint
- Logging for all incoming requests
- Interactive API docs at `/docs`
- GET endpoints to retrieve stored invoices

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure authentication (optional):
```bash
# Edit .env file and set your bearer token
API_BEARER_TOKEN=your-secure-token-here
```

## Running the Server

Start the server locally:
```bash
python3 main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available locally at `http://localhost:8000`

## Authentication

All POST endpoints require a bearer token in the `Authorization` header.

**Default token:** `your-secret-token-here`

Change this in the `.env` file or by setting the `API_BEARER_TOKEN` environment variable.

## API Endpoints

### GET /
Root endpoint with API information (no authentication required)

### GET /health
Health check endpoint (no authentication required)

### POST /data
Accepts JSON data wrapped in a `data` field (requires authentication)

Example request:
```bash
curl -X POST http://localhost:8000/data \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-token-here" \
  -d '{"data": {"name": "John", "email": "john@example.com"}}'
```

### POST /data/raw
Accepts any JSON structure directly and saves to database (requires authentication)

Example request:
```bash
curl -X POST http://localhost:8000/data/raw \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer kevin_reform_sample_token" \
  -d '{
  "file_name": "invoice_001.pdf",
  "invoice_number": "IV97308789",
  "invoice_date": "01/13/2025",
  "total_amount": 1532.58,
  "ct_number": "CT640896",
  "mot": "LCL",
  "office": "EU",
  "direction": "EXPORT",
  "calculated_code": 1402
}'
```

### GET /invoices
Retrieves all invoices from the database (requires authentication)

Query parameters:
- `limit`: Max records to return (default: 100, max: 1000)
- `offset`: Number of records to skip (default: 0)

Example request:
```bash
curl http://localhost:8000/invoices?limit=50&offset=0 \
  -H "Authorization: Bearer kevin_reform_sample_token"
```

### GET /invoices/{invoice_number}
Retrieves a specific invoice by invoice number (requires authentication)

Example request:
```bash
curl http://localhost:8000/invoices/IV97308789 \
  -H "Authorization: Bearer kevin_reform_sample_token"
```

## Interactive Documentation

FastAPI provides automatic interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Exposing with Ngrok

1. Install ngrok:
```bash
brew install ngrok  # On macOS
```

2. Configure ngrok with your authtoken:
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

3. Start ngrok tunnel:
```bash
ngrok http 8000
```

4. Use the provided public URL to access your endpoint from anywhere

**Current Public URL:** `https://unpicturesquely-stylar-annice.ngrok-free.dev`

Example:
```bash
curl -X POST https://unpicturesquely-stylar-annice.ngrok-free.dev/data/raw \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer kevin_reform_sample_token" \
  -d '{
  "file_name": "invoice_001.pdf",
  "invoice_number": "IV97308789",
  "invoice_date": "01/13/2025",
  "total_amount": 1532.58,
  "ct_number": "CT640896",
  "mot": "LCL",
  "office": "EU",
  "direction": "EXPORT",
  "calculated_code": 1402
}'
```

**Note:** This URL will change when ngrok is restarted unless you create a free static domain at https://dashboard.ngrok.com/domains

## Security Notes

- The default token is `your-secret-token-here` - change this before exposing to the internet
- Use environment variables or the `.env` file to set a secure token
- Invalid authentication attempts are logged with a truncated token for security
- Public endpoints (/, /health) do not require authentication
