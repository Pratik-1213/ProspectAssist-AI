# ProspectAssist AI

**AI-Powered Lending Lead Intelligence & Scoring Platform**

ProspectAssist AI is an end-to-end intelligent lending analytics platform designed for financial institutions, NBFCs, and loan officers. It evaluates applicant risk profiles using multi-factor underwriting algorithms, credit bureau metrics, FOIR penalty thresholds, and real-time behavioral intent.

---

## Key Features

- **Automated Lead Scoring Engine**: Calculates multi-factor borrower creditworthiness (salary stability, average balances, EMI repayment history, FOIR ratios, and spending discipline).
- **Behavioral Intent Tracking**: Factors in app sessions, loan calculator interactions, and document downloads.
- **FastAPI Core Architecture**: Asynchronous RESTful APIs with JWT authentication, WebSocket live progress broadcasts, and audit logging.
- **Interactive Loan Officer Dashboard**: Real-time triage, eligibility simulation, and automated applicant categorization.
- **Audit Logging & Compliance**: Structured audit trails logging administrative evaluations and score adjustments.

---

## System Architecture

```
ProspectAssist-AI/
├── backend/
│   ├── main.py                # FastAPI endpoints & WebSocket router
│   ├── database.py            # SQLite repository & schema initialization
│   ├── models.py              # Pydantic schemas & data models
│   ├── services/
│   │   ├── scoring_service.py # Underwriting scoring algorithm
│   │   ├── auth_service.py    # JWT authentication & passlib hashing
│   │   └── ai_service.py      # LLM reasoning & risk narrative generator
│   └── tests/
│       └── test_scoring.py    # Automated test suite
└── frontend/                  # React + Vite Loan Officer Console
```

---

## Getting Started

### 1. Prerequisites
- Python 3.9+
- Node.js 18+

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### 3. Running Automated Tests
```bash
cd backend
python -m pytest tests
```
