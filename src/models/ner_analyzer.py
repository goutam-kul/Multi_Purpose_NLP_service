# src/models/ner_analyzer.py
from ollama import Client
import json
import sys
from src.exceptions.custom_exceptions import ModelConnectionError, JSONParsingError, NLPServiceException
from src.cache.cache_manager import cache_response, CacheConfig
from src.config.config import config

class NERAnalyzer:
    def __init__(self):
        try:
            self.client = Client(host=config.ollama_host)
            self.model = config.model_paths["ner"]
        except Exception as e:
            raise ModelConnectionError(f"Failed to initialize Ollama client: {str(e)}")

    @cache_response(prefix="ner", expire=CacheConfig.TEST_EXPIRE if "pytest" in sys.modules else CacheConfig.NER_EXPIRE)
    def analyze(self, text: str, options: dict = None) -> dict:
        try:
            prompt = f"""You are a Named Entity Recognition system. Extract entities from the text and return ONLY a valid JSON object.
Format EXACTLY like this:
{{
    "entities": [
        {{"text": "John", "type": "PERSON", "start": 0, "end": 4}},
        {{"text": "Microsoft", "type": "ORG", "start": 11, "end": 20}},
        {{"text": "Seattle", "type": "LOC", "start": 24, "end": 31}}
    ]
}}

RULES:
1. Entity types must be: PERSON, ORG, LOC, or OTHER
2. Start/end indices must match actual positions in text
3. Return ONLY the JSON object, nothing else
4. Ensure proper JSON formatting

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
                start = raw_text.find('{')
                end = raw_text.rfind('}') + 1
                
                if start == -1 or end == 0:
                    raise JSONParsingError("No JSON object found in response")
                
                json_str = raw_text[start:end]
                result = json.loads(json_str)

                # Format the final response
                analysis = {
                    "text": text,
                    "entities": result["entities"]
                }
                
                return analysis
                
            except json.JSONDecodeError as e:
                raise JSONParsingError(f"Failed to parse model response: {str(e)}")
            
        except Exception as e:
            raise NLPServiceException(f"Error in NER analysis: {str(e)}")