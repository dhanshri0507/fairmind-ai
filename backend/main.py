from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import scan, explain, simulate, report

app = FastAPI(
    title="FairMind AI",
    description="AI Bias Detection and Mitigation Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router, prefix="/api")
app.include_router(explain.router, prefix="/api")
app.include_router(simulate.router, prefix="/api")
app.include_router(report.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "FairMind AI Backend is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
