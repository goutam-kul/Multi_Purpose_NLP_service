from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, List, Literal, Any


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
        max_length=1000,  # Reasonable length for sentiment analysis
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
                "explanation": "Strong positive sentiment expressed through 'really enjoyed'"
            }
        }
    )
    
    text: str
    sentiment: Literal["POSITIVE", "NEGATIVE", "NEUTRAL"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str

# --------------------------------------------------------------------------------------------------------------

# NER Reponse
class NERRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "John works at Microsoft in Seattle",
                "options": {"include_positions": True}
            }
        }
    )
    text: str = Field(
        ..., 
        min_length=1,
        max_length=2000,  # NER typically can handle longer texts
        description="Input text for entity recognition (max 2000 characters)"
    )
    options: Optional[Dict] = Field(
        default=None,
        description="Optional parameters for NER analysis"
    )

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Text cannot be empty or whitespace only")
        # Additional validation could check for at least one word
        if len(v.split()) < 2:
            raise ValueError("Text must contain at least two words for meaningful NER analysis")
        return v


class NERResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "John works at Microsoft in Seattle",
                "entities": [
                    {"text": "John", "type": "PERSON", "start": 0, "end": 4},
                    {"text": "Microsoft", "type": "ORG", "start": 11, "end": 20},
                    {"text": "Seattle", "type": "LOC", "start": 24, "end": 31}
                ]
            }
        }
    )
    text: str = Field(..., description="Original input text")
    entities: List[Dict[str, Any]] = Field(
        ...,
        description="List of identified entities with their positions and types"
    )

    @field_validator('entities')
    @classmethod
    def validate_entities(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for entity in v:
            required_fields = {'text', 'type', 'start', 'end'}
            if not all(field in entity for field in required_fields):
                raise ValueError(f"Entity must contain all required fields: {required_fields}")
            if entity['start'] >= entity['end']:
                raise ValueError("Entity end position must be greater than start position")
            if not isinstance(entity['text'], str):
                raise ValueError("Entity text must be a string")
        return v

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
                "original_text": "Original long text...",
                "summary": "Concise summary...",
                "metadata": {
                    "original_length": 100,
                    "summary_length": 30,
                    "compression_ratio": 0.7
                },
                "key_points": ["Point 1", "Point 2", "Point 3"]
            }
        }
    )
    
    original_text: str
    summary: str
    metadata: Dict
    key_points: List[str]

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
                "explanation": "Focus on technological innovation in automotive industry"
            }
        }
    )
    
    text: str
    primary_category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    all_categories: List[CategoryResult]  # Using the new CategoryResult model
    explanation: str