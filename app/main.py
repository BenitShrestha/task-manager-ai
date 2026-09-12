from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.limiter import limiter
from app.routers import ai, auth, tasks

app = FastAPI(title="AI-Powered Task Manager API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(ai.router)


@app.get("/health")
def health():
    return {"status": "ok"}