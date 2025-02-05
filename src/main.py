from fastapi import FastAPI
from src.api.router import router
from src.exceptions.custom_exceptions import NLPServiceException
from src.api.error_handler import nlp_exception_handler

app = FastAPI(
    title="Multi-Purpose NLP service",
    description="""
    A comprehensive Natural Language Processing API providing multiple text analysis services:
    
    
    ## Features
    * 📊 Sentiment Analysis - Analyze text sentiment with confidence scores
    * 🎯 Named Entity Recognition (NER) - Identify and classify named entities
    * 📝 Text Classification - Categorize text into predefined categories
    * 📚 Text Summarization - Generate concise summaries of longer texts
    
    
    ## Key Benefits
    * Fast response times with Redis caching
    * Detailed response metadata
    * Configurable options for each service
    * Compreshensive error handling
    """,
    version="1.0.0",
    contact={
        "name": "Goutam",
        "email": "goutammunda3134@gmail.com",
        "url": "https://github.com/goutam-kul/Multi_Purpose_NLP_service"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/license/MIT"
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Register exception handler
app.add_exception_handler(NLPServiceException, nlp_exception_handler)

# Add router
app.include_router(router=router,
    prefix="/api/v1",
    tags=["NLP Services"]
)

@app.get("/",
        tags=["Root"],
        summary="API Root",
        description="Welcome endpoints with links to API documentation")
async def root():
    return {
        "message": "Welcome to Multi-Purpose NLP service.",
        "documentation": {
            "Swagger UI": "/docs",
            "ReDoc": "/redoc",
            "OpenAPI JSON": "/api/v1/openapi.json"
        },
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app, host="0.0.0.0", port=8000)