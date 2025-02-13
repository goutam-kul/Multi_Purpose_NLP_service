from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.api.models import  (
    ModelSelection,
    SentimentRequest,
    SentimentResponse,
    NERRequest, 
    NERResponse, 
    TextClassificationRequest,
    TextClassificationResponse, 
    SummarizationRequest, 
    SummarizationResponse,
)
from src.models.sentiment_analyzer import SentimentAnalyzer
from src.models.ner_analyzer import NERAnalyzer
from src.models.text_summarizer import TextSummarizer
from src.models.text_classifier import TextClassifier
from src.exceptions.custom_exceptions import NLPServiceException
from typing import Dict, Any
from src.config.config import AVAILABLE_MODELS, config
from src.cache.cache_manager import CacheManager

router = APIRouter()

class  LazyModelLoader:
    """Lazy loader for LLM to prevent loading all models at startup casusin OOM"""
    def __init__(self):
        self._sentiment = None
        self._ner = None
        self._summarizer = None
        self._classifier = None

    @property
    def sentiment_analyzer(self):
        if self._sentiment is None:
            self._sentiment = SentimentAnalyzer()
        return self._sentiment
    
    @property
    def ner_analyzer(self):
        if self._ner is None:
            self._ner = NERAnalyzer()
        return self._ner
    
    @property
    def summarizer(self):
        if self._summarizer is None:
            self._summarizer = TextSummarizer()
        return self._summarizer
    
    @property
    def classifier(self):
        if self._classifier is None:
            self._classifier = TextClassifier()
        return self._classifier

    def cleanup(self):
        """Clean up loaded models"""
        self._sentiment = None
        self._ner = None
        self._summarizer = None
        self._classifier = None

# Initialize lazy loader
models = LazyModelLoader()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(input_data: SentimentRequest):
    try:
        cleaned_text = input_data.text.strip('"')
        result = models.sentiment_analyzer.analyze(cleaned_text, input_data.options)
        return result
    except NLPServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/ner", response_model=NERResponse)
async def analyze_ner(input_data: NERRequest):
    try: 
        result = models.ner_analyzer.analyze(input_data.text, input_data.options)  # Removed options parameter
        return result
    except NLPServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/summarize", response_model=SummarizationResponse)
async def summarize_text(request: SummarizationRequest):
    try:
        result = models.summarizer.summarize(request.text, request.options)
        return result
    except NLPServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    

@router.post("/classify", response_model=TextClassificationResponse)
async def classify_text(request: TextClassificationRequest):
    try:
        result = models.classifier.classify(request.text, request.options)
        return result
    except NLPServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
@router.post("/set-model")
async def set_model(selection: ModelSelection):
    """Set the model to use for all NLP services"""
    if config.set_current_model(selection.model_name):
        print(f"Model changed to: {config.get_current_model()}")  # Debug
        return {
            "status": "success",
            "message": f"Model set to {selection.model_name}",
            "current_model": config.get_current_model()
        }
    raise HTTPException(
        status_code=400,
        detail=f"Invalid model name. Available models: {list(AVAILABLE_MODELS.keys())}"
    )

@router.get("/available-models")
async def get_available_models():
    """Get list of available models"""
    return {
        "models": AVAILABLE_MODELS,
        "current_model": config.get_current_model()
    }  