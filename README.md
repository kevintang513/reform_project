
# Reform project

Automation Link: [Automation Link](https://app.reformhq.com/automations/69434710459edeea6d973334/edit)
View Link: [View Link](https://app.reformhq.com/views/694356c7459edeea6d97aaf0)
Loom Recording: [Loom Link](https://www.loom.com/share/6181e89473914107af2bcfbc46bb5d2b)

# How to run the automation:

Send an email with the relevant attachments to the following email address to automatically trigger the automation: email+69434710459edeea6d973334@reformhq.com.

Alternatively, you can use the run history to replay a previous run.

# Design overview:
I designed the automation to be as simple as possible with a focus on interpretability and ease of use for both technical and non-technical users.

To start it is triggered via email send to a specific email.

Subsequently, I extract the data using a custom shape that has the following fields:
- file_name
- ct_number
- invoice_number
- invoice_data
- total_amount
The custom shape's fields had additional descriptions to help both users and the system understand the data better.

After the data was extracted with the custom shape, I took an additional step to format and clean the data using a transform node. In this node I was able to specify a target JSON format, as well as add additional instructions to ensure the CT number field was properly formatted.

I then included a validation step to ensure the CT field was properly captured from the document.

Subsequently there is an enrich node using the csv table to match the ct number with the MOT, Office, and Direction. I specificed that if no match was found, the system should return null for the MOT, Office, and Direction fields, which would then be caught by the exception node that followed.

Lastly, I used a transform node to calculate the calculated_code field based on the MOT, Office, and Direction fields. I separated the instructions into different steps for the first 2 digits, and for the last 2 digits for easy organization, in case additional fields/digits needed to be added in the future. 

# Assumptions:
To be honest there weren't any assumptions I needed to make for this project, I thought that the instructions were very clear in the requirements.

# Improvements:
With more time I would make the following improvements:

Improve the details of this readme/documentation as well as refine the loom recording to show how the API recieves the data using ngrok.
Do additional testing with additional attachment types to explore additional edge cases and test automation robustness.

# Bugs:
CSV link had some issues, causing the loss of a good chunk of time to first understand that the issues was with improper reading, and then receiving a link that worked.




# JSON POST Endpoint API - How to start the service and run the integration
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

Or access it via ngrok at `https://unpicturesquely-stylar-annice.ngrok-free.dev`

## Authentication

All POST endpoints require a bearer token in the `Authorization` header.

**Default token:** `your-secret-token-here`

Change this in the `.env` file or by setting the `API_BEARER_TOKEN` environment variable.

The actual token will be sent securely to authorized users.

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



## Security Notes

- The default token is `your-secret-token-here` - change this before exposing to the internet.
- Use environment variables or the `.env` file to set a secure token
- Invalid authentication attempts are logged with a truncated token for security
- Public endpoints (/, /health) do not require authentication
