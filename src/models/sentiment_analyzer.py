from ollama import Client
import json
import sys
from typing import Dict, Optional
from src.exceptions.custom_exceptions import (
    NLPServiceException,
    ModelConnectionError,
    InvalidModelResponseError,
    ValidationError,
    JSONParsingError
)
from src.cache.cache_manager import cache_response, CacheConfig
from src.config.config import config

class SentimentAnalyzer:
    def __init__(self):
        try:
            self.client = Client(host=config.ollama_host)
            self.model = config.model_paths["sentiment"]
        except Exception as e:
            raise ModelConnectionError(f"Failed to initialize Ollama client: {str(e)}")
            
    def _validate_input(self, text: str) -> None:
        """Validate input text"""
        if not text:  # Catches emtpy string
            raise ValidationError("Input text cannot be empty")
        if not isinstance(text, str):
            raise ValidationError("Input must be a string")
        if len(text.split()) == 0: # Catches whitespace "  "
            raise ValidationError("Input text cannot be whitespaces only")
        
    def _validate_response(self, result: Dict) -> None:
        """Validate model response"""
        required_fields = ["sentiment", "confidence", "explanation"]
        for field in required_fields:
            if field not in result:
                raise InvalidModelResponseError(f"Missing required field in model response: {field}")
            
        if result["sentiment"] not in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
            raise InvalidModelResponseError(f"Invalid sentiment value: {result['sentiment']}")
        
        if not isinstance(result['confidence'], (int, float)) or not 0<= result['confidence'] <=1:
            raise InvalidModelResponseError(f"Invalid confidence score : {result['confidence']}")
        
    @cache_response(prefix="sentiment", expire=CacheConfig.TEST_EXPIRE if "pytest" in sys.modules else CacheConfig.SENTIMENT_EXPIRE)
    def analyze(self, text: str, options: Optional[Dict] = None) -> dict:
        try:
            # Validate input 
            self._validate_input(text=text)
            prompt = f"""You are a sentiment analyzer. Return ONLY a valid JSON object.
Format EXACTLY like this (including the curly braces):
{{
    "sentiment": "POSITIVE/NEGATIVE/NEUTRAL",
    "confidence": 0.9,
    "explanation": "Brief explanation here"
}}

RULES:
1. sentiment must be EXACTLY one of: POSITIVE, NEGATIVE, or NEUTRAL
2. confidence must be a number between 0 and 1
3. explanation must be one SHORT sentence
4. Return ONLY the JSON object, nothing else
5. Ensure the JSON has proper closing braces

Analyze this text: "{text}"
"""
            try:
                response = self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    stream=False
                )
            except Exception as e:
                raise ModelConnectionError(f"Failed to get model response: {str(e)}")
                
            try:
                # Extract JSON object
                raw_text = response['response']
                
                # Find the JSON part
                start = raw_text.find('{')
                end = raw_text.rfind('}') + 1
                
                if start == -1 or end == 0:
                    raise JSONParsingError("No JSON object found in response")
                
                json_str = raw_text[start:end]
                result = json.loads(json_str)

                # Validate the response
                self._validate_response(result=result)
                
                # Format the final response
                analysis = {
                    "text": text,
                    "sentiment": result["sentiment"],
                    "confidence": round(float(result["confidence"]), 4),
                    "explanation": str(result["explanation"])
                }
                
                return analysis
                
            except json.JSONDecodeError as e:
                raise JSONParsingError(f"Failed to parse model response: {str(e)}")
            
        except Exception as e:
            # If it's our custom exception re-raise it
            if isinstance(e, (ValidationError, ModelConnectionError,
                              InvalidModelResponseError, JSONParsingError)):
                raise 
            # Otherwise wrap it in a general error
            raise NLPServiceException(f"Unexpected error in sentiment analysis: {str(e)}")