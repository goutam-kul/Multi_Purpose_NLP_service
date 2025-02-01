from ollama import Client
import json

class NERAnalayzer:
    def __init__(self):
        self.client = Client(host="http://localhost:11434")
        self.model = "phi3:latest"  

    def analyze(self, text:str, options: dict = None) -> dict:
        try:
            prompt = f"""You are a Named Entity Recognition (NER) system. Indentify entities in the text and return ONLY a valid JSON boject.
Format EXACTLY like this (including the curly braces):
{{
    "entities": [
        {{
            "text": "entity text",
            "type": "PERSON/ORG/LOC/DATE/TIME/OTHER",
            "start": start_index,
            "end": end_index
        }}]
}}
RULES:
1. entity type must be one of: PERSON, ORG (organization), LOC(location), DATE, TIME or OTHER.
2. start and end should be a character indices in the text.
3. Return ONLY the JSON boject, nothing else.
4. Include ALL entities found
5. Ensure proper JSON formatting

Text to analyze: "{text}"
"""
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )

            print("Raw Response:", response['response'])

            try:
                # Extract JSON object
                raw_text = response['response']
                start = raw_text.find('{')
                end = raw_text.rfind('}') + 1

                if start == -1 and end == 0:
                    raise Exception("No JSON object found in response")
                
                json_str = raw_text[start:end]
                result = json.loads(json_str)

                # Validate the response
                if not isinstance(result.get("entities"), list):
                    raise ValueError("Response must contain 'entities' array")
                
                # Format the final response
                analysis = {
                    "text": text,
                    "entities": result["entities"]
                }

                return analysis
            
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                print(f"Attempted to parse: {json_str}")
                raise Exception("Failed to parse the model response as valid JSON")
            
        except Exception as e:
            raise Exception(f"Error in the NER analysis: {str(e)}")