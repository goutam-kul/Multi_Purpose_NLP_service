from fastapi import FastAPI
from src.api.router import router
from src.exceptions.custom_exceptions import NLPServiceException
from src.api.error_handler import nlp_exception_handler

app = FastAPI(
    title="Multi-Purpose NLP service",
    description="A service that provides various NLP functionality",
    version="1.0.0"
)

# Register exception handler
app.add_exception_handler(NLPServiceException, nlp_exception_handler)

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