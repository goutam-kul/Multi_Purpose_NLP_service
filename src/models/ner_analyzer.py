# src/models/ner_analyzer.py
from ollama import Client
import json
import sys
from src.exceptions.custom_exceptions import ModelConnectionError, JSONParsingError, NLPServiceException
from src.cache.cache_manager import cache_response, CacheConfig
from src.config.config import config
from typing import Optional, Dict

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
            # Process options
            extract_time = options.get('extract_time', False) if options else False
            extract_numerical = options.get('extract_numerical', False) if options else False
            extract_email = options.get('extract_email', False) if options else False

            # Build entity type instructions based on options
            entity_types = """ENTITY DEFINITIONS:
- PERSON: Names of people (e.g., John Smith)
- ORG: Companies, institutions (e.g., Microsoft, NASA)
- LOC: Locations, places (e.g., Seattle, Mount Everest)"""

            if extract_time:
                entity_types += "\n- TIME: Time expressions (e.g., 2:30 PM, morning, evening)"
            if extract_numerical:
                entity_types += "\n- NUMBER: Numerical values (e.g., 42, thousand, million)"
            if extract_email:
                entity_types += "\n- EMAIL: Email addresses (e.g., user@example.com)"

            prompt = f"""You are a Named Entity Recognition (NER) expert. Return ONLY a valid JSON object.
CRITICAL RULES:
1. ONLY extract entities that EXACTLY match the input text
2. Double-check each entity against the original text before including
3. Do NOT hallucinate or infer entities not present in text
4. Count positions from 0, including spaces and punctuation
5. Handle multilingual text (including non-ASCII characters) correctly
6. Verify each entity's position matches the text exactly

{entity_types}

# Special handling for multilingual text:
- Count UTF-8 characters properly
- Include full character sequences for names/places
- Preserve original text exactly as it appears

VALIDATION STEPS:
1. Extract potential entity
2. Verify it exists in original text using exact string match
3. Calculate start/end positions
4. Validate positions by checking text[start:end] == entity
5. Only include if ALL checks pass

FORMAT:
{{
    "entities": [
        {{
            "text": "exact entity text",
            "type": "PERSON/ORG/LOC/NUMBER/TIME/EMAIL",
            "start": exact_start_position,
            "end": exact_end_position,
            "confidence": 0.0 to 1.0
        }}
    ]
}}

Text to analyze: "{text}"

BEFORE RETURNING:
1. Verify each entity exists in text
2. Confirm positions by text[start:end]
3. Remove any unverified entities
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
                print(f"Raw Reponse: {raw_text}")
                if start == -1 or end == 0:
                    raise JSONParsingError("No JSON object found in response")
                
                json_str = raw_text[start:end]
                result = json.loads(json_str)

                # Validate entities 
                result["entities"] = self._validate_entities(text=text, entities=result["entities"])

                print(f"JSON: {json_str}")
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