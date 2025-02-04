from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.api.models import SentimentRequest, SentimentResponse
from src.api.models import NERRequest, NERResponse
from src.api.models import SummarizationRequest, SummarizationResponse
from src.api.models import TextClassificationRequest, TextClassificationResponse
from src.models.sentiment_analyzer import SentimentAnalyzer
from src.models.ner_analyzer import NERAnalyzer
from src.models.text_summarizer import TextSummarizer
from src.models.text_classifier import TextClassifier
from src.exceptions.custom_exceptions import NLPServiceException
from typing import Dict, Any

router = APIRouter()

# Initialize models
try: 
    sentiment_analyzer = SentimentAnalyzer()
    ner_analyzer = NERAnalyzer("ner_tinyllama_lora")
    summarizer = TextSummarizer()
    classifier = TextClassifier()
except Exception as e:
    print(f"Error initializing models: {str(e)}")
    raise


@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(input_data: SentimentRequest):
    try:
        result = sentiment_analyzer.analyze(input_data.text, input_data.options)
        return result
    except NLPServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/ner", response_model=NERResponse)
async def analyze_ner(input_data: NERRequest):
    try: 
        result = ner_analyzer.analyze(input_data.text, input_data.options)
        return result
    except NLPServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@router.post("/summarize", response_model=SummarizationResponse)
async def summarize_text(request: SummarizationRequest):
    try:
        result = summarizer.summarize(request.text, request.options)
        return result
    except NLPServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    

@router.post("/classify", response_model=TextClassificationResponse)
async def classify_text(request: TextClassificationRequest):
    try:
        result = classifier.classify(request.text, request.options)
        return result
    except NLPServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")