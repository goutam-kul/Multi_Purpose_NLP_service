from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class TextInput(BaseModel):
    text: str
    task: str
    options: Optional[Dict] = None

    class config:
        jason_schema_extra = {
            "example": {
                "text": "I love this product! It works perfectly.",
                "task": "sentiment_analysis",
                "options": {"return_all_scores": True}
            }
        }


# Text-Summarization
class SummarizationRequest(BaseModel):
    text: str
    options: Optional[Dict[str, Any]] = None

class SummarizationResponse(BaseModel):
    original_text: str
    summary: str
    metadata: Dict[str, Any]
    key_points: List[str]


# Text-Classification
class CategoryScore(BaseModel):
    category: str
    confidence: float

class TextClassificationRequest(BaseModel):
    text: str
    options: Optional[Dict[str, Any]] = None

class TextClassificationResponse(BaseModel):
    text: str
    primary_category: str
    confidence: float
    all_categories: List[CategoryScore]
    explanation: str