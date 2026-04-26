# FairMind AI

> AI Bias Detection & Mitigation Platform — Google Build with AI · Solution Challenge 2026

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square)](https://react.dev)
[![Gemini](https://img.shields.io/badge/AI-Gemini%201.5%20Pro-4285F4?style=flat-square)](https://ai.google.dev)

## Features
- 📊 Upload CSV and detect bias across multiple protected attributes
- ⚖️ Fairness metrics: Demographic Parity Gap, Equalized Odds Gap
- 🤖 Gemini-powered explanations in **Technical** or **Plain English** mode
- 🧪 Mitigation simulator: Reweighing, Threshold Tuning, Equalized Odds
- 🗄️ Audit history stored in Supabase

## Project Structure
```
FairMind-AI/
├── backend/
│   ├── main.py                  # FastAPI app entry
│   ├── requirements.txt
│   ├── Procfile                 # Railway deployment
│   ├── .env                     # Secrets (not committed)
│   ├── models/
│   │   └── request_models.py
│   ├── routers/
│   │   ├── scan.py              # POST /api/scan
│   │   ├── explain.py           # POST /api/explain
│   │   ├── simulate.py          # POST /api/simulate
│   │   └── report.py            # GET  /api/report/{id}
│   └── services/
│       ├── fairness.py          # fairlearn engine
│       ├── gemini.py            # Gemini 1.5 Pro
│       └── firestore.py         # Supabase client
├── frontend/
│   ├── src/
│   │   ├── api/client.js
│   │   ├── components/
│   │   │   ├── UploadHub.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── MetricCard.jsx
│   │   │   ├── CasualToggle.jsx
│   │   │   └── Simulator.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   └── index.html
└── supabase_schema.sql
```

## Quick Start

### Backend
```bash
cd backend
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend runs at http://localhost:8000  
Swagger docs at http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at http://localhost:5173

## Environment Variables

### backend/.env
```
GEMINI_API_KEY=your_key
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_anon_key
```

### frontend/.env
```
VITE_API_URL=http://localhost:8000
```

## Deployment

| Service | Purpose | Config |
|---------|---------|--------|
| Railway | Backend | Set env vars in Railway dashboard |
| Vercel  | Frontend | Set `VITE_API_URL` to Railway URL |

## Supabase Setup
Run `supabase_schema.sql` in the Supabase SQL editor to create the `audits` table.
