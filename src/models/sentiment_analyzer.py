from ollama import Client
import json

class SentimentAnalyzer:
    def __init__(self):
        self.client = Client(host="http://localhost:11434")
        self.model = "llama3.2:3b"  
        
    def analyze(self, text: str, options: dict = None) -> dict:
        try:
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
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )
            
            print("Raw Response:", response['response'])
            
            try:
                # Extract JSON object
                raw_text = response['response']
                
                # Find the JSON part
                start = raw_text.find('{')
                end = raw_text.rfind('}') + 1
                
                if start == -1 or end == 0:
                    raise Exception("No JSON object found in response")
                
                json_str = raw_text[start:end]
                result = json.loads(json_str)
                
                # Validate the response
                if result["sentiment"] not in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
                    raise ValueError(f"Invalid sentiment value: {result['sentiment']}")
                
                if not isinstance(result["confidence"], (int, float)) or not 0 <= result["confidence"] <= 1:
                    raise ValueError(f"Invalid confidence value: {result['confidence']}")
                
                # Format the final response
                analysis = {
                    "text": text,
                    "sentiment": result["sentiment"],
                    "confidence": round(float(result["confidence"]), 4),
                    "explanation": str(result["explanation"])
                }
                
                return analysis
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Attempted to parse: {json_str}")
                raise Exception("Failed to parse model response as valid JSON")
            
        except Exception as e:
            raise Exception(f"Error in sentiment analysis: {str(e)}")