# Analytics Dashboard Backend

## Overview
Python backend service for fetching and persisting Google Analytics data.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment configuration:
```bash
cp .env.example .env
```

3. Configure your Google Analytics credentials in `.env`

## Project Structure

```
backend/
├── app/
│   ├── config/          # Configuration settings
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   └── main.py          # FastAPI app
├── requirements.txt
└── README.md
```

## Development

```bash
# Run the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```