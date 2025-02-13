from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from typing import Optional, Dict, List, Literal, Any

# Model selection
class ModelSelection(BaseModel):
    model_name: str

# Sentiment 
class SentimentRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "I love this product!",
                "options": {"include_metadata": True}
            }
        }
    )
    text: str = Field(
        ..., 
        min_length=1,
        max_length=500,  # Reasonable length for sentiment analysis
        description="Input text to analyze (max 1000 characters)"
    )
    options: Optional[Dict] = Field(
        default=None,
        description="Optional parameters for sentiment analysis"
    )

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Text cannot be empty or whitespace only")
        return v


class SentimentResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "I really enjoyed this product!",
                "sentiment": "POSITIVE",
                "confidence": 0.95,
                "explanation": "Strong positive sentiment expressed through 'really enjoyed'",
                "metadata": {
                    "sentiment_breakdown": {
                        "positive_words": ["enjoyed"],
                        "negative_words": [],
                        "intensifiers": ["really"]
                    },
                    "processing_time_seconds": 20
                }
            }
        }
    )
    
    text: str
    sentiment: Literal["POSITIVE", "NEGATIVE", "NEUTRAL"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    model: str
    metadata: Optional[Dict] = None
# --------------------------------------------------------------------------------------------------------------

# NER 
class NERRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "John works at Microsoft in Seattle",
                "options": {
                    "extract_time": True,  # Extract time expressions
                    "extract_numerical": True,  # Extract numbers and quantities
                    "extract_email": True  # Extract email addresses
                }
            }
        }
    )
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Input text for entity recognition (max 2000 characters)"
    )
    options: Optional[Dict] = Field(
        default=None,
        description="Optional features: extract_time, extract_numerical, extract_email"
    )

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        # Remove leading/trailing whitespace
        v = v.strip()
        
        # Check for empty or whitespace
        if not v:
            raise ValueError("Text cannot be empty or whitespace only")
        
        # Check minimum word count (for meaningful NER)
        if len(v.split()) < 2:
            raise ValueError("Text must contain at least two words for meaningful NER analysis")
            
        return v

class EntityModel(BaseModel):
    text: str
    type: str  
    start: int
    end: int
    confidence: float = Field(default=0.85)  # Default confidence if not provided

class NERResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "SpaceX is located in USA",
                "entities": [
                    {
                        "text": "USA",
                        "type": "LOC",
                        "start": 21,
                        "end": 24,
                        "confidence": 0.99
                    }
                ]
            }
        }
    )
    text: str
    entities: List[EntityModel]
    model: str
#----------------------------------------------------------------------------------------------------------------

# Summarization 
class SummarizationRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "Your long text to summarize goes here...",
                "options": {"max_length": 150, "type": "abstractive"}
            }
        }
    )
    
    text: str = Field(..., min_length=10, description="Text to summarize")
    options: Optional[Dict] = Field(
        default=None,
        description="Summarization options like max_length, type"
    )

    @field_validator('text')
    @classmethod
    def validate_text_length(cls, v: str) -> str:
        v = v.strip()
        if len(v.split()) < 10:
            raise ValueError("Text must be at least 10 words long for summarization")
        return v

class SummarizationResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "summary": "Concise summary...",
                "metadata": {
                    "original_length": 100,
                    "summary_length": 30,
                    "compression_ratio": 0.7
                },
                "key_points": ["Point 1", "Point 2", "Point 3"],
                "model": "qwen2.5:3b"
            }
        }
    )
    
    original_text: str
    summary: str
    metadata: Dict
    key_points: List[str]
    model: str

#---------------------------------------------------------------------------------------------------------------

# Text Classification 
class TextClassificationRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "Text to classify",
                "options": {
                    "categories": ["Business", "Technology", "Science"],
                    "multi_label": False
                }
            }
        }
    )
    
    text: str = Field(..., min_length=1, description="Text to classify")
    options: Optional[Dict] = Field(
        default=None,
        description="Classification options like categories, multi_label"
    )

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Text cannot be empty or whitespace only")
        return v

class CategoryResult(BaseModel):
    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)

class TextClassificationResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "Tesla announces new electric car model",
                "primary_category": "Technology",
                "confidence": 0.85,
                "all_categories": [
                    {"category": "Technology", "confidence": 0.85},
                    {"category": "Business", "confidence": 0.60}
                ],
                "explanation": "Focus on technological innovation in automotive industry",
                "model": "llama3.2:3b"
            }
        }
    )
    
    text: str
    primary_category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    all_categories: List[CategoryResult]  # Using the new CategoryResult model
    explanation: str
    model: str