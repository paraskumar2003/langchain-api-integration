from fastapi import FastAPI, Request
from .router.index import router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

app = FastAPI(
    title="LangChain GPT API",
    description="A structured FastAPI service to get JSON output from GPT",
    version="1.0.0"
)

# Mount router
app.include_router(router, prefix="/api", tags=["Chat"])

# Create the limiter — using client IP address as the key
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Register global exception handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app = FastAPI()

# Attach limiter to app
app.state.limiter = limiter

# Middleware to limit payload size
MAX_BODY_SIZE = 1024 * 1024  # 1 MB
@app.middleware("http")
async def limit_payload_size(request: Request, call_next):
    body = await request.body()
    if len(body) > MAX_BODY_SIZE:
        raise HTTPException(status_code=413, detail="Payload too large (limit 1 MB)")
    # Recreate the request stream (since .body() consumes it)
    request._receive = lambda: {"type": "http.request", "body": body, "more_body": False}
    return await call_next(request)

@app.get("/")
def root():
    return {"message": "LangChain GPT API running"}
