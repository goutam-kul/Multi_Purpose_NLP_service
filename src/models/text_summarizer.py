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


    def clean_currency_numbers(self, text: str) -> str:
        """Clean currency and number formatting"""
        import re
        
        # Fix currency amounts
        text = re.sub(r'\$(\d+\.?\d*)', r'$\1 ', text)
        
        # Fix number formatting
        text = re.sub(r'(\d+\.?\d*)billion', r'\1 billion', text)
        text = re.sub(r'(\d+\.?\d*)million', r'\1 million', text)
        
        # Remove duplicate spaces
        text = ' '.join(text.split())
        
        return text 
        
    @cache_response(prefix="summarize", expire=CacheConfig.TEST_EXPIRE if "pytest" in sys.modules else CacheConfig.SUMMARIZE_EXPIRE)
    def summarize(self, text: str, options: dict = None) -> dict:
        try:
            self.model = config.get_current_model()
            # Set default options 
            if options is None:
                options = {}

            max_length = options.get('max_length', 150)
            sum_type = options.get('type', 'abstractive')

            prompt = f"""You are a text summarizer focusing on maximum information density. Return ONLY a valid JSON object.
FORMAT exactly like this (including the curly braces):
{{
    "summary": "The generated summary here",
    "length": 120,
    "compression_ratio": 0.65,
    "key_points": ["Point 1", "Point 2", "Point 3"]
}}

STRICT RULES:
1. Generate a {sum_type} summary
2. CRITICAL: Summary be MUST EXACTLY {max_length} words - not more 
3. Ensure the summary is coherent and grammatically correct
4. Include 3 key points that capture main ideas
5. Return ONLY the JSON object
6. Ensure proper JSON formatting

SUMMARIZATION STRATEGY:
1. First identify the key information
2. Construct sentences that use exactly {max_length} words total
3. If summarization  exceeds {max_length} words, it is an ERROR
4. Each sentence should convey complete ideas
5. Use connecting words to ensure flow
6. Count words carefully to match the limit exactly

FORMAT CHECK:
1. Count every word in your summary
2. For max_length = 50, summary should contain EXACTLY 50 words
3. Validate word count before returning

Example of good length usage:
For limit 50 words:
"AI technology transforms healthcare through improved diagnostics and treatment planning. Machine learning algorithms analyze patient data to predict outcomes. Researchers develop new drug discovery methods while hospitals implement automated systems for efficient patient care."

Text to summarize: {text}
"""
            response = self.client.generate(
                prompt=prompt,
                model=self.model,
                stream=False
            )
            print(f"Raw Reponse: {response}")
            try:
                # Extract the JSON object
                raw_text = response['response']
                start = raw_text.find('{')
                end = raw_text.rfind('}') + 1

                if start == -1 or end == 0:
                    raise Exception("No JSON object found in response")
                
                json_str = raw_text[start:end]
                result = json.loads(json_str)

                # Clean currency and numbers
                result['summary'] = self.clean_currency_numbers(result['summary'])

                # Validate response
                if not result.get("summary"):
                    raise InvalidModelResponseError("Missing summary in model response")
                
                if not result.get("key_points"):
                    raise InvalidModelResponseError("Missing Key points in model response")

                # Calculate original text length
                original_length = len(text.split())
                summary_length = len(result['summary'].split())
                compression_ratio = round(1 - (summary_length/original_length), 2) if original_length > 0 else 0

                print(f"Response after validation: {result}")
                analysis = {
                    "original_text": text,
                    "summary": result['summary'],
                    "metadata": {
                        "original_length": original_length,
                        "summary_length": summary_length,
                        "compression_ratio": compression_ratio,
                        "summary_type": sum_type
                    },
                    "key_points": result['key_points'],
                    "model": self.model
                }

                print(f"Analysis: {analysis}")

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