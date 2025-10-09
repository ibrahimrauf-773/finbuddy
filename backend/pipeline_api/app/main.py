from fastapi import FastAPI
from app.api.v1 import api_router

app = FastAPI(title="Finance Code API", debug=True)  # <-- debug=True

app.include_router(api_router)

@app.get("/")
def health():
    return {"status": "ok"}
