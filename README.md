# FairMind AI 🧠⚖️

> **AI Bias Detection & Mitigation Platform**  
> Built for Google Build with AI · Solution Challenge 2026

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%200.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Build-Vite-646CFF?style=flat-square&logo=vite)](https://vitejs.dev)
[![Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-4285F4?style=flat-square&logo=google)](https://ai.google.dev)
[![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E?style=flat-square&logo=supabase)](https://supabase.com)
[![Railway](https://img.shields.io/badge/Backend%20Host-Railway-0B0D0E?style=flat-square&logo=railway)](https://railway.app)
[![Vercel](https://img.shields.io/badge/Frontend%20Host-Vercel-000000?style=flat-square&logo=vercel)](https://vercel.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## 🚀 What is FairMind AI?

FairMind AI is a full-stack platform that empowers developers, data scientists, and organizations to **detect, understand, and mitigate bias** in machine learning models — with zero ML expertise required.

Upload a CSV dataset, select your protected attributes, and FairMind AI will:
- Compute fairness metrics across demographic groups
- Generate a plain-English or professional explanation powered by **Gemini 2.5 Flash**
- Simulate the effect of bias mitigation strategies before you retrain
- Export a **professional PDF audit report**
- Store all audit history in **Supabase** for accountability

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **Bias Scanner** | Upload any CSV; detect bias across multiple protected attributes (gender, race, age, etc.) |
| ⚖️ **Fairness Metrics** | Demographic Parity Gap, Equalized Odds Gap, Selection Rate per group |
| 🤖 **Gemini Explainer** | Switch between **Technical** (professional audit) and **Plain English** (casual) explanation modes |
| 🧪 **Mitigation Simulator** | Simulate Reweighing, Threshold Tuning, and Equalized Odds — see metric improvements instantly |
| 📄 **PDF Report Export** | Download a formatted audit report with charts and findings via ReportLab |
| 🗄️ **Audit History** | Every scan saved to Supabase with full metadata for traceability |
| 🔄 **Model Fallback Chain** | Auto-retries Gemini 2.0 Flash → 1.5 Flash → static fallback on quota errors (429 handling) |

---

## 🗂️ Project Structure

```
FairMind-AI/
├── backend/                        # FastAPI backend (deployed on Railway)
│   ├── main.py                     # App entry point, CORS, router registration
│   ├── requirements.txt            # Pinned Python dependencies
│   ├── Procfile                    # Railway start command
│   ├── railway.json                # Railway build configuration
│   ├── nixpacks.toml               # Nixpacks Python 3.12 pin
│   ├── .python-version             # Python version for Railway
│   ├── sample_data.csv             # Demo dataset for testing
│   ├── models/
│   │   └── request_models.py       # Pydantic request/response schemas
│   ├── routers/
│   │   ├── scan.py                 # POST /api/scan  — bias detection
│   │   ├── explain.py              # POST /api/explain — Gemini explanations
│   │   ├── simulate.py             # POST /api/simulate — mitigation simulation
│   │   └── report.py              # POST /api/report  — PDF report generation
│   └── services/
│       ├── fairness.py             # fairlearn engine (metrics + mitigation)
│       ├── gemini.py               # Gemini API with multi-model fallback chain
│       ├── firestore.py            # Supabase client (lazy-init, audit storage)
│       └── prediction_simulator.py # Deterministic bias simulation engine
├── frontend/                       # React + Vite frontend (deployed on Vercel)
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js           # Axios API client
│   │   ├── components/
│   │   │   ├── UploadHub.jsx       # CSV upload + attribute selection
│   │   │   ├── Dashboard.jsx       # Metrics display + charts + explainer
│   │   │   ├── MetricCard.jsx      # Reusable fairness metric card
│   │   │   ├── CasualToggle.jsx    # Technical / Plain English mode toggle
│   │   │   └── Simulator.jsx       # Mitigation simulator + chart + PDF download
│   │   ├── App.jsx                 # Main app with routing logic
│   │   ├── App.css
│   │   └── index.css               # Global styles (glassmorphism, dark theme)
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── supabase_schema.sql             # SQL to create the audits table
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- A [Gemini API key](https://aistudio.google.com/app/apikey)
- A [Supabase](https://supabase.com) project

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# Create backend/.env (see Environment Variables section)
uvicorn main:app --reload
```
- **API:** http://localhost:8000  
- **Swagger Docs:** http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install

# Create frontend/.env (see Environment Variables section)
npm run dev
```
- **App:** http://localhost:5173

---

## 🔑 Environment Variables

### `backend/.env`
```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL_NAME=gemini-2.5-flash    # optional, falls back automatically
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### `frontend/.env`
```env
VITE_API_URL=http://localhost:8000
```

---

## 🌐 Deployment

| Service | Purpose | Notes |
|---|---|---|
| **Railway** | Backend (FastAPI) | Set all `backend/.env` variables in Railway dashboard; uses Nixpacks with Python 3.12 |
| **Vercel** | Frontend (React) | Set `VITE_API_URL` to your Railway backend URL |
| **Supabase** | Database | Run `supabase_schema.sql` in the SQL editor to create the `audits` table |

### Railway Quick Deploy
1. Push `backend/` to a GitHub repo (or use the full repo)
2. Create a new Railway project → connect GitHub
3. Set environment variables in Railway dashboard
4. Railway auto-detects `Procfile` and starts `uvicorn`

### Vercel Quick Deploy
1. Import your GitHub repo into Vercel
2. Set **Root Directory** to `frontend`
3. Add `VITE_API_URL` environment variable
4. Deploy!

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/scan` | Upload CSV + config → returns bias metrics |
| `POST` | `/api/explain` | Audit results → Gemini explanation |
| `POST` | `/api/simulate` | Simulate mitigation strategy |
| `POST` | `/api/report` | Generate & return PDF audit report |
| `GET` | `/health` | Health check |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI 0.115, Python 3.12, Uvicorn |
| **AI** | Google Gemini 2.5 Flash (+ 2.0 Flash / 1.5 Flash fallback) |
| **Fairness** | fairlearn 0.10, scikit-learn 1.5, pandas 2.2, numpy 1.26 |
| **Database** | Supabase (PostgreSQL) |
| **PDF** | ReportLab 4.1 |
| **Frontend** | React 18, Vite, Axios |
| **Hosting** | Railway (backend), Vercel (frontend) |

---

## 🗄️ Supabase Setup

Run `supabase_schema.sql` in the Supabase SQL editor to create the `audits` table:

```bash
# Or paste the contents into: Supabase Dashboard → SQL Editor → New Query → Run
```

The table stores: `id`, `created_at`, `filename`, `protected_attribute`, `label_column`, `metrics` (JSONB), and `explanation`.

---

## 📁 Sample Data

`backend/sample_data.csv` is a synthetic hiring dataset with columns:
- `age`, `gender`, `race`, `education`, `experience`, `hired` (label)

Use it to test the full bias detection → explain → simulate → report flow.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  Built with ❤️ for <strong>Google Build with AI · Solution Challenge 2026</strong>
</div>
