from datetime import datetime
from fastapi.responses import HTMLResponse
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Lingora API",
        "timestamp": datetime.now()
    }, 200
