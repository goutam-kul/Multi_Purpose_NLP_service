from ollama import Client
import json
import sys
from src.exceptions.custom_exceptions import ModelConnectionError, JSONParsingError, NLPServiceException
from src.cache.cache_manager import cache_response, CacheConfig
from src.config.config import config
from typing import Optional, Dict
from src.exceptions.custom_exceptions import (
    NLPServiceException,
    JSONParsingError,
    ValidationError,
    ModelConnectionError,
    InvalidModelResponseError
)

class NERAnalyzer:
    def __init__(self):
        try:
            self.client = Client(host=config.ollama_host)
            self.model = config.model_paths["ner"]
        except Exception as e:
            raise ModelConnectionError(f"Failed to initialize Ollama client: {str(e)}")
        
    def _validate_entities(self, text: str, entities: list) -> list:
        validated = []

        for entity in entities:
            if entity['text'] not in text:
                continue

            # Vefiry positions
            start = entity.get('start')
            end = entity.get('end')
            if start is not None and end is not None:
                if text[start:end] != entity['text']:
                    # Recalculate entity positions
                    start = text.find(entity['text'])
                    end = start + len(entity['text'])
                    entity['start'] = start
                    entity['end'] = end 

            # Add confidence if not present
            if "confidence" not in entity or entity['confidence'] is None:
                entity['confidence'] = 0.85
            else:
                entity['confidence'] = round(entity['confidence'])
            
            validated.append(entity)
        return validated

    @cache_response(prefix="ner", expire=CacheConfig.TEST_EXPIRE if "pytest" in sys.modules else CacheConfig.NER_EXPIRE)
    def analyze(self, text: str, options: Optional[Dict] = None) -> dict:
        try:
            # Initialize options
            if options is None:
                options = {}
                
            # Base entity types we always want
            allowed_types = {'PERSON', 'ORG', 'LOC'}
            
            # Add optional types based on options
            if options.get('extract_time', False):
                allowed_types.add('TIME')
            if options.get('extract_numerical', False):
                allowed_types.add('NUMBER')
            if options.get('extract_email', False):
                allowed_types.add('EMAIL')

            # Build entity type definitions
            entity_types = """ENTITY DEFINITIONS AND EXTRACTION RULES:
    - PERSON: Full names of people only (e.g., John Smith, Mary Johnson)
    - ORG: Organizations, companies, institutions, brands (e.g., Microsoft, NASA,)
    - LOC: Places, cities, countries, locations (e.g., New York, Mount Everest, Japan)"""

            if options.get('extract_time', False):
                entity_types += "\n- TIME: Time expressions, clock times, periods (e.g., 2:30 PM, morning, 9AM)"
            if options.get('extract_numerical', False):
                entity_types += "\n- NUMBER: Numerical values, quantities, measurements (e.g., 42, million, 12.5)"
            if options.get('extract_email', False):
                entity_types += "\n- EMAIL: Valid email addresses (e.g., user@example.com)"

            prompt = f"""You are a precise Named Entity Recognition (NER) expert. Return ONLY a valid JSON object.

    {entity_types}
    - IMPORTANT: Remember you are an expert in finding NAME and ENTITIES from text, Extract them from the given text as precisely as possible.
    
    CRITICAL RULES:
    0. Identify NAMES and ENTITIES correctly, DO NOT make Errors
    1. ONLY extract entities from the types defined above
    2. Each entity MUST include: text, type, start, end, confidence
    3. Entity text MUST match the input text exactly
    4. Positions (start/end) must be accurate character positions
    5. Skip single pronouns, articles, and common words
    6. Confidence should reflect certainty of entity type
    7. Check entity types carefully for each entities 
    8. DO NOT make mistakes like classifying EMAIL as ORG type entity 

    OUTPUT FORMAT:
    {{
        "entities": [
            {{
                "text": "exact matched text",
                "type": "one of the defined types",
                "start": exact_start_position,
                "end": exact_end_position,
                "confidence": confidence_score
            }}
        ]
    }}

    Text to analyze: "{text}"
    """
            # Get response from model
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )
            try: 
                # Process response
                raw_text = response['response']
                start = raw_text.find('{')
                end = raw_text.rfind('}') + 1
                
                if start == -1 or end == 0:
                    raise JSONParsingError("No JSON object found in response")
                    
                result = json.loads(raw_text[start:end])
                
                # Filter entities by allowed types
                result["entities"] = [
                    entity for entity in result["entities"]
                    if entity.get('type') in allowed_types
                ]
                
                # Validate entities
                result["entities"] = self._validate_entities(text, result["entities"])
                
                return {
                    "text": text,
                    "entities": result["entities"]
                }
            except json.JSONDecodeError as e:
                raise JSONParsingError(f"Failed to parse model response: {str(e)}")
            
        except Exception as e:
            # If it's our custom exception re-raise it
            if isinstance(e, (ValidationError, ModelConnectionError,
                              InvalidModelResponseError, JSONParsingError)):
                raise 
            # Otherwise wrap it in a general error
            raise NLPServiceException(f"Unexpected error in sentiment analysis: {str(e)}")