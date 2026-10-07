# Bulk Certificate Generator API

A high-performance, resilient backend API built with FastAPI for asynchronously generating, tracking, and retrieving professional PDF certificates in bulk.

---

## 1. Project Overview

The **Bulk Certificate Generator API** enables organizations and event managers to generate personalized certificates of completion for hundreds of recipients through a single API submission. 

Key capabilities:
- **Single Bulk Request**: Accepts an event name, issue date, and an array of recipient details in one HTTP call.
- **Strict Data Validation**: Validates recipient names, email addresses, and event dates before queuing jobs.
- **Asynchronous Bulk Processing**: Offloads PDF generation to background workers so the API responds instantly with a job identifier.
- **Granular Status & Progress Tracking**: Real-time tracking of pending, completed, and failed certificates.
- **Fault-Isolated Execution**: Individual certificate generation failures (e.g., malformed data or rendering errors) do not halt or disrupt the remainder of the bulk job.
- **Direct PDF Retrieval**: Secure endpoints to list and download completed PDF certificates.
- **Interactive Documentation**: Auto-generated OpenAPI / Swagger UI at `/docs`.

---

## 2. Technology Stack

This project strictly adheres to student-friendly, local, open-source technologies with zero external paid APIs:

* **Python 3.11+**: Modern, typed Python.
* **FastAPI**: Asynchronous web framework for high-throughput REST APIs.
* **SQLAlchemy 2.0**: Robust ORM for data modeling and transactional safety.
* **SQLite**: Embedded relational database requiring zero external service setup.
* **Pydantic V2**: Request body validation and response serialization.
* **ReportLab**: Native Python library for pixel-perfect PDF certificate rendering.
* **FastAPI BackgroundTasks**: Built-in background task processing without Redis or Celery dependencies.
* **Pytest**: Automated testing framework with full isolation and mocking support.
* **Ruff**: Modern Python linter for clean, idiomatic code.

---

## 3. Project Structure

```
Bulk Certificate Generator API/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point & CORS
│   ├── api/
│   │   ├── router.py            # API V1 router aggregation
│   │   └── routes/
│   │       ├── jobs.py          # /jobs endpoints (create, status, list certs)
│   │       └── certificates.py  # /certificates endpoints (PDF download)
│   ├── core/
│   │   ├── config.py            # App settings and directory paths
│   │   └── database.py          # SQLAlchemy engine, session maker, get_db
│   ├── models/
│   │   ├── __init__.py
│   │   ├── job.py               # GenerationJob entity & statuses
│   │   └── certificate.py       # CertificateRecord entity
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── job.py               # Pydantic schemas for jobs
│   │   └── certificate.py       # Pydantic schemas for recipients/certs
│   ├── services/
│   │   ├── job_service.py       # Database CRUD operations
│   │   └── certificate_service.py # ReportLab PDF template generator
│   └── workers/
│       └── tasks.py             # Resilient background bulk processor
├── generated/                   # Directory where generated PDF files are stored
├── tests/
│   ├── conftest.py              # Pytest fixtures and DB isolation setup
│   ├── test_jobs.py             # Job creation and status progress tests
│   ├── test_validation.py       # Input validation tests (422 responses)
│   ├── test_generation.py       # PDF file generation and signature tests
│   ├── test_failure_handling.py # Fault isolation tests for failed recipients
│   └── test_retrieval.py        # PDF retrieval and 400/404 error tests
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## 4. Setup & Installation

### Step 1: Clone or Navigate to the Repository

```bash
cd "c:/Users/Harsha Vardhan/Downloads/Bulk Certificate Generator API"
```

### Step 2: Create a Virtual Environment

**On Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Running the Application

Start the local Uvicorn development server:

```bash
uvicorn app.main:app --reload
```

The server starts at `http://127.0.0.1:8000`.

---

## 6. API Documentation

Interactive Swagger documentation is available out of the box:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 7. API Usage & Examples

### 1. Create a Bulk Generation Job

**Endpoint**: `POST /api/v1/jobs`

**cURL Command**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "AI Workshop 2026",
    "certificate_date": "2026-10-07",
    "recipients": [
      {
        "name": "Rahul Kumar",
        "email": "rahul@example.com",
        "course": "AI Engineering"
      },
      {
        "name": "Priya Sharma",
        "email": "priya@example.com",
        "course": "AI Engineering"
      }
    ]
  }'
```

**Response (HTTP 201 Created)**:
```json
{
  "job_id": "4b92b6a2-9b28-4efc-8b2f-2f92f25d97ad",
  "status": "queued",
  "total": 2
}
```

---

### 2. Check Job Status & Progress

**Endpoint**: `GET /api/v1/jobs/{job_id}`

**cURL Command**:
```bash
curl "http://127.0.0.1:8000/api/v1/jobs/4b92b6a2-9b28-4efc-8b2f-2f92f25d97ad"
```

**Response (HTTP 200 OK)**:
```json
{
  "job_id": "4b92b6a2-9b28-4efc-8b2f-2f92f25d97ad",
  "status": "completed",
  "total": 2,
  "completed": 2,
  "failed": 0,
  "pending": 0,
  "event_name": "AI Workshop 2026",
  "certificate_date": "2026-10-07",
  "created_at": "2026-10-07T17:30:00.000000",
  "completed_at": "2026-10-07T17:30:01.250000"
}
```

**Job Statuses**:
- `queued`: Submitted and awaiting worker pickup.
- `processing`: Background generation is actively running.
- `completed`: All certificates generated successfully.
- `completed_with_errors`: Some certificates succeeded, while some failed.
- `failed`: All certificate generations failed.

---

### 3. List Certificates for a Job

**Endpoint**: `GET /api/v1/jobs/{job_id}/certificates`

**cURL Command**:
```bash
curl "http://127.0.0.1:8000/api/v1/jobs/4b92b6a2-9b28-4efc-8b2f-2f92f25d97ad/certificates"
```

**Response (HTTP 200 OK)**:
```json
[
  {
    "id": "e67e6c38-71e8-4228-b8ce-39d3ca8fb687",
    "job_id": "4b92b6a2-9b28-4efc-8b2f-2f92f25d97ad",
    "recipient_name": "Rahul Kumar",
    "recipient_email": "rahul@example.com",
    "course": "AI Engineering",
    "status": "completed",
    "file_path": "C:\\...\\generated\\certificate_e67e6c38-71e8-4228-b8ce-39d3ca8fb687.pdf",
    "error_message": null,
    "created_at": "2026-10-07T17:30:00.000000",
    "download_url": "/api/v1/certificates/e67e6c38-71e8-4228-b8ce-39d3ca8fb687"
  },
  {
    "id": "a18f4502-3932-4753-90d2-9b168fe283f1",
    "job_id": "4b92b6a2-9b28-4efc-8b2f-2f92f25d97ad",
    "recipient_name": "Priya Sharma",
    "recipient_email": "priya@example.com",
    "course": "AI Engineering",
    "status": "completed",
    "file_path": "C:\\...\\generated\\certificate_a18f4502-3932-4753-90d2-9b168fe283f1.pdf",
    "error_message": null,
    "created_at": "2026-10-07T17:30:00.000000",
    "download_url": "/api/v1/certificates/a18f4502-3932-4753-90d2-9b168fe283f1"
  }
]
```

---

### 4. Download a Generated Certificate PDF

**Endpoint**: `GET /api/v1/certificates/{certificate_id}`

**cURL Command**:
```bash
curl -O -J "http://127.0.0.1:8000/api/v1/certificates/e67e6c38-71e8-4228-b8ce-39d3ca8fb687"
```

- Returns the PDF binary with header `Content-Type: application/pdf`.
- If the certificate failed generation, returns `400 Bad Request` with the error description.
- If the certificate ID does not exist, returns `404 Not Found`.

---

## 8. Running Automated Tests

Run the full test suite using Pytest:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Run linter checks:

```bash
ruff check .
```

---

## 9. Design Decisions & Architecture

### 1. Why FastAPI?
- **Speed & Simplicity**: Built on Starlette and Pydantic, providing asynchronous performance, strict typing, and automatic OpenAPI schema documentation.
- **Built-in BackgroundTasks**: Allows clean, in-process asynchronous task offloading without introducing heavy external infrastructure like Redis or Celery.

### 2. Why SQLite & SQLAlchemy 2.0?
- **Zero Infrastructure Dependency**: SQLite runs as a local file, making the project 100% self-contained and reproducible on any machine.
- **Transactional Integrity**: SQLAlchemy 2.0 handles unit-of-work transactions, ensuring that certificate records and job counters remain synchronized even when individual generation errors occur.

### 3. Why ReportLab?
- **Pure Python PDF Rendering**: ReportLab requires no external system binaries (unlike tools that require headless Chrome or `wkhtmltopdf`).
- **Precision & Speed**: Allows programmatic creation of vectors, fonts, decorative borders, and text placement in milliseconds per certificate.

### 4. Why FastAPI BackgroundTasks?
- **Lightweight Asynchrony**: For bulk jobs, users should receive their `job_id` immediately rather than waiting synchronously for dozens or hundreds of PDFs to render. `BackgroundTasks` executes in the background of the application process with zero external service overhead.

### 5. Why Is Each Certificate Processed Independently?
- **Fault Isolation**: In a batch of 500 recipients, if recipient #25 has a malformed character, unrenderable font glyph, or disk write glitch, the remaining 499 certificates must still be generated.
- Each certificate is wrapped in an individual `try-except` block. A failure marks the certificate record as `failed`, records the error message, increments the `failed_count`, and continues processing subsequent recipients.

### 6. Why Two Database Entities?
- **GenerationJob (1)**: Tracks high-level batch metadata (`event_name`, `certificate_date`, `status`, `total_count`, `completed_count`, `failed_count`, `completed_at`).
- **CertificateRecord (N)**: Tracks individual recipient metadata, status (`pending`, `processing`, `completed`, `failed`), individual file paths, and failure messages.
- This separation gives O(1) job status polling while still preserving full inspection of individual recipient outcomes.

### 7. How Progress is Tracked
- The `pending` count is computed deterministically as:
  $$\text{pending} = \max(0, \text{total\_count} - (\text{completed\_count} + \text{failed\_count}))$$
- As the background worker proceeds, it atomically commits progress after each certificate. The client can poll `GET /api/v1/jobs/{job_id}` at any interval to inspect real-time progress.
