from ollama import Client
import json
import sys
import time
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
        
    def _extract_sentiment_features(self, text: str) -> Dict:
        positive_words = ["good", "great", "amazing", "excellent",
                         "love", "loved", "loving" "wonderful", "fantastic", "enjoyed", "happy"]
        negative_words = ["bad", "terrible", "awful", "awfully", "horrendous", "unpleasant"
                         "horrible", "hate", "disappointed", "poor", "worst"]
        intensifiers = ["very", "really", "extremely", "absolutely", "totally", "completely"]
        
        # Conver to lower case for matching 
        text_lower = text.lower()
        words = text_lower.split()

        # Find matches
        found_positives = [word for word in words if word in positive_words]
        found_negatives = [word for word in words if word in negative_words]
        found_intensifiers = [word for word in words if word in intensifiers]

        return {
            "positive_words": found_positives,
            "negative_words": found_negatives,
            "intensifiers": found_intensifiers
        }
        
    @cache_response(prefix="sentiment", expire=CacheConfig.TEST_EXPIRE if "pytest" in sys.modules else CacheConfig.SENTIMENT_EXPIRE)
    def analyze(self, text: str, options: Optional[Dict] = None) -> dict:
        try:
            start_time = time.time()
            # Get current model from config
            current_model = config.get_current_model()
            self.model = current_model
            print(f'Using model: {self.model}')  # Debug 

            include_metadata = options.get('include_metadata', False) if options else False
            prompt = f"""You are an expert sentiment analyzer with advanced capabilities in detecting genuine emotions and sarcasm. Return ONLY a valid JSON object.

Format EXACTLY like this (including the curly braces):
{{
    "sentiment": "POSITIVE/NEGATIVE/NEUTRAL",
    "confidence": 0.9,
    "explanation": "Brief explanation here"
}}

ANALYSIS GUIDELINES:
1. First, look for genuine emotional indicators:
   - Consistent tone throughout the text
   - Multiple positive/negative aspects mentioned
   - Natural language patterns
   - Specific details supporting the sentiment

2. Sarcasm Analysis (require MULTIPLE signals):
   NEGATIVE Sarcasm:
   - Uses exaggerated positive words ("perfect", "amazing", "just great")
   - Followed by explicit negative situations
   - Example: "Just perfect! The food was cold and service was terrible"
   -> NEGATIVE sentiment (false praise with clear negative context)

   POSITIVE Sarcasm:
   - Uses seemingly negative words or criticism
   - But implies actual satisfaction or praise
   - Example: "Worst decision ever to buy this! Now I can't stop using it"
   -> POSITIVE sentiment (mock criticism with clear positive context)

IMPORTANT RULES:
1. Genuine enthusiasm is NOT sarcasm
2. Multiple positive words without contradictions = genuine positive
3. Don't assume sarcasm without clear contradictory evidence
4. Exclamation marks can indicate genuine excitement

EXAMPLES:
Genuine Positive:
"I absolutely love this restaurant! The food is amazing and the service is perfect!"
-> POSITIVE (consistent praise with multiple specific positives)

EXAMPLES:
Negative Sarcasm:
"Oh brilliant! Another day waiting 2 hours for customer service!"
-> NEGATIVE (false praise with negative situation)

Positive Sarcasm:
"Terrible product, now my life is too efficient and I have too much free time!"
-> POSITIVE (mock criticism with positive outcome)

Ambigous Sarcasm:
"Thanks for 'fixing' my laptop, now it's running slower than ever!"
-> NEGATIVE (sarcastic gratitude with negative outcome)
"Oh no, free food at work again? I can’t believe they’re torturing us like this!"
-> POSITIVE (showing false ordeal)

Mixed:
"Food was great but the service was slow"
-> NEUTRAL (balanced positive and negative elements)

RULES:
1. Sentiment must be EXACTLY one of: POSITIVE, NEGATIVE, or NEUTRAL
2. Confidence must be a number between 0 and 1
3. Explanation must be one SHORT sentence
4. Return ONLY the JSON object, nothing else
5. Ensure proper JSON formatting

Analyze this text: "{text}"
"""
            try:
                response = self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    stream=False
                )
                print(f"Using Model: {self.model}")
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
                
                processing_time = int((time.time() - start_time))

                # Format the final response
                analysis = {
                    "text": text,
                    "sentiment": result["sentiment"],
                    "confidence": round(float(result["confidence"]), 4),
                    "explanation": str(result["explanation"]),
                    "model": self.model
                }
                if include_metadata:
                    # Extract sentiment features
                    sentiment_features = self._extract_sentiment_features(text=text)
                    
                    analysis["metadata"] = {
                        "sentiment_breakdown": sentiment_features,
                        "processing_time_seconds": processing_time
                    }
                    
                print(f"Resonse: {analysis}")
                
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