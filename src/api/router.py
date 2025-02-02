from fastapi import APIRouter, HTTPException
from src.api.models import TextInput
from src.api.models import SummarizationRequest, SummarizationResponse
from src.api.models import TextClassificationRequest, TextClassificationResponse
from src.models.sentiment_analyzer import SentimentAnalyzer
from src.models.ner_analyzer import NERAnalyzer
from src.models.text_summarizer import TextSummarizer
from src.models.text_classifier import TextClassifier
from typing import Dict

router = APIRouter()
sentiment_analyzer = SentimentAnalyzer()
ner_analyzer = NERAnalyzer("ner_tinyllama_lora")
summarizer = TextSummarizer()
classifier = TextClassifier()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/analyze")
async def analyze_text(input_data: TextInput) -> Dict:
    print(f"Received request with task: {input_data.task}")
    try:
        if input_data.task == "sentiment_analysis":
            print("Processing Sentiment Analaysis request")
            return sentiment_analyzer.analyze(
                input_data.text,
                input_data.options
            )
        elif input_data.task == "ner":
            print("Processing NER request")
            return ner_analyzer.analyze(
                input_data.text,
                input_data.options
            )
        else:
            raise HTTPException(
                status_code=400,
                detial=f"Task '{input_data.task}' not supported yet."
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/summarize", response_model=SummarizationResponse)
async def summarize_text(request: SummarizationRequest):
    try:
        result = summarizer.summarize(request.text, request.options)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/classify", response_model=TextClassificationResponse)
async def classify_text(request: TextClassificationRequest):
    try:
        result = classifier.classify(request.text, request.options)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))