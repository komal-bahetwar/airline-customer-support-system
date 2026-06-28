from fastapi import FastAPI

app = FastAPI(
    title="AI-Powered Airline Customer Support System",
    description="Backend API for Airline Customer Support",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to AI-Powered Airline Customer Support System!"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }