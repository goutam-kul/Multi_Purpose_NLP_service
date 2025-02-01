from fastapi import FastAPI
from api.router import router

app = FastAPI(
    title="Multi-Purpose NLP service",
    description="A service that provides various NLP functionality",
    version="1.0.0"
)

# Add router
app.include_router(router=router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Multi-Purpose NLP service.",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app, host="0.0.0.0", port=6000)