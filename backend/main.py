# backend/main.py

from fastapi import FastAPI

# LOCAL
# from backend.core.init_model import load_model
# from backend.routers import news

# RENDER
from core.init_model import load_model
from routers import news

import uvicorn

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    app.state.model, app.state.tokenizer = load_model()

app.include_router(news.router, prefix="/news", tags=["news"])

if __name__ == "__main__":
    uvicorn.run("main.app", host = "0.0.0.0", port = 10000, reload = True)