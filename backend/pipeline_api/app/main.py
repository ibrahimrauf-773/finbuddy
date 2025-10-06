from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 👇 this line imports your new router (the /v1/entries endpoint)
from app.api.v1.entries import router as entries_router

app = FastAPI(title="FinBuddy API")

# Allow requests from anywhere for now (for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple health + root endpoints stay
@app.get("/")
def root():
    return {"message": "FinBuddy API running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# 👇 this line connects your /v1/entries endpoint to the app
app.include_router(entries_router, prefix="/v1")
