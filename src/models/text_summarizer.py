from ollama import Client
import json
import sys
from src.cache.cache_manager import CacheConfig, cache_response
from src.config.config import config
from src.exceptions.custom_exceptions import (
    NLPServiceException,
    ModelConnectionError,
    InvalidModelResponseError,
    ValidationError,
    JSONParsingError
)


class TextSummarizer:
    def __init__(self):
        self.client = Client(host=config.ollama_host)
        self.model = config.model_paths["summarize"]

    @cache_response(prefix="summarize", expire=CacheConfig.TEST_EXPIRE if "pytest" in sys.modules else CacheConfig.SUMMARIZE_EXPIRE)
    def summarize(self, text: str, options: dict = None) -> dict:
        try:
            # Set default options 
            if options is None:
                options = {}

            max_length = options.get('max_length', 150)
            sum_type = options.get('type', 'abstractive')

            prompt = f"""You are a text summarizer. Return ONLY a valid JSON object. 
FORMAT exactly like this (including the curly braces):
{{
    "summary": "The generated summary here",
    "length": 120,
    "compression_ratio": 0.65,
    "key_points": ["Point 1", "Point 2", "Point 3"]
}}

RULES:
1. Generate a {sum_type} summary
2. Keep summary under {max_length} words
3. Include 2-3 kep points
4. Return ONLY the JSON object, nothing else
5. Ensure proper JSON formatting with closing braces

Text to summarize: {text}
"""
            response = self.client.generate(
                prompt=prompt,
                model=self.model,
                stream=False
            )
            try:
                # Extract the JSON object
                raw_text = response['response']
                start = raw_text.find('{')
                end = raw_text.rfind('}') + 1

                if start == -1 or end == 0:
                    raise Exception("No JSON object found in response")
                
                json_str = raw_text[start:end]
                result = json.loads(json_str)

                # Validate response
                if not result.get("summary"):
                    raise InvalidModelResponseError("Missing summary in model response")
                
                if not result.get("key_points"):
                    raise InvalidModelResponseError("Missing Key points in model response")

                # Calculate original text length
                original_length = len(text.split())
                summary_length = len(result['summary'].split())
                compression_ratio = round(1 - (summary_length/original_length), 2) if original_length > 0 else 0

                analysis = {
                    "original_text": text,
                    "summary": result['summary'],
                    "metadata": {
                        "original_length": original_length,
                        "summary_length": summary_length,
                        "compression_ratio": compression_ratio,
                        "summary_type": sum_type
                    },
                    "key_points": result['key_points']
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