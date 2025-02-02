from ollama import Client
import json

class TextClassifier:
    def __init__(self):
        self.client = Client(host="http://localhost:11434")
        self.model = "llama3.2:3b"
        self.default_categories = [
            "Business", "Technology", "Politics", "Sports",
            "Entertainment", "Science", "Health", "Education"
        ]
        
    def classify(self, text: str, options: dict = None) -> dict:
        """
        Classify text into predefined categories
        
        Args:
            text (str): Input text to classify
            options (dict, optional): Configuration options including:
                - categories (list): Custom categories to classify into
                - multi_label (bool): Allow multiple category assignments
        
        Returns:
            dict: Contains predicted categories and confidence scores
        """
        try:
            if options is None:
                options = {}
                
            categories = options.get('categories', self.default_categories)
            multi_label = options.get('multi_label', False)
            
            categories_str = ", ".join(categories)
            multi_label_str = "multiple categories" if multi_label else "single category"
            
            prompt = f"""You are a text classifier. Return ONLY a valid JSON object.
Format EXACTLY like this (including the curly braces):
{{
    "primary_category": "Category name" , # MUST be string, not object
    "confidence": 0.85,
    "all_categories": [
        {{"category": "Category1", "confidence": 0.85}},
        {{"category": "Category2", "confidence": 0.45}}
    ],
    "explanation": "Brief explanation for the classification"
}}

RULES:
1. Classify into these categories only: {categories_str}
2. Return {multi_label_str}
3. Confidence Scoring: 
    - Main category: 0.7-0.9 confidence
    - Related categories: 0.4-0.8 confidence
    - Minimum difference between related categories: 0.1
    - Maximum difference between related categories: 0.3
    - NEVER use extreme splits (>0.5 difference)

CONTEN RULES:
1. Entertainment:
    - Media companies (e.g., Netflix, Disney)
    - Gaming and interactive content
    - Content creation and disribution
2. Technology:
    - Digital platforms
    - Gaming technology 
    - Interactive systems
3. Business:
    - Acquisitions and mergers
    - Financial transactions
    - Corporate startegy

EXAMPLE 1:
Input: "Disney launches new streaming platform with AI recommendations"
Output: {{
    "primary_category": "Entertainment",
    "confidence": 0.85,
    "all_categories": [
        {{"category": "Entertainment", "confidence": 0.85}},
        {{"category": "Technology", "confidence": 0.70}},
        {{"category": "Business", "confidence": 0.55}}
    ],
    "explanation": "Primary focus is entertainment (streaming), with significant technology aspect (AI) and business implications"
}} 

Text to classify: "{text}"
"""
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )
            
            try:
                # Extract JSON object
                raw_text = response['response']
                start = raw_text.find('{')
                end = raw_text.rfind('}') + 1
                
                if start == -1 or end == 0:
                    raise Exception("No JSON object found in response")
                
                json_str = raw_text[start:end]
                result = json.loads(json_str)
                
                # Validate response
                if not result.get("primary_category") in categories:
                    raise ValueError(f"Invalid primary category: {result['primary_category']}")
                    
                for cat in result.get("all_categories", []):
                    if not cat.get("category") in categories:
                        raise ValueError(f"Invalid category: {cat.get('category')}")
                
                # Format the final response
                analysis = {
                    "text": text,
                    "primary_category": result["primary_category"],
                    "confidence": round(float(result["confidence"]), 3),
                    "all_categories": [
                        {
                            "category": cat["category"],
                            "confidence": round(float(cat["confidence"]), 3)
                        }
                        for cat in result["all_categories"]
                    ],
                    "explanation": result["explanation"]
                }
                
                return analysis
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Attempted to parse: {json_str}")
                raise Exception("Failed to parse model response as valid JSON")
            
        except Exception as e:
            raise Exception(f"Error in text classification: {str(e)}")