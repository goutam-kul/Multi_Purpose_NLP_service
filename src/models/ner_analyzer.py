from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig
import torch
import json
import re

class NERAnalyzer:
    def __init__(self, model_path: str = "./ner_tinyllama_lora"):
        self.entity_types = {"PERSON": "PERSON", 
                        "ORGANIZATION": "ORG", 
                        "LOCATION": "LOC", 
                        "MISCELLANEOUS": "OTHER"}
        
        # Load the tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        # Load base model for CPU
        base_model = AutoModelForCausalLM.from_pretrained(
            "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            device_map="cpu",  # Explicitly set to CPU
            trust_remote_code=True
        )
        
        # Load the PEFT adapter
        self.model = PeftModel.from_pretrained(
            base_model,
            model_path,
            is_trainable=False
        )
        self.model.eval()

    def _parse_model_output(self, output: str, original_text: str) -> list:
        entities = []
        pattern = r'\[(.*?): (.*?)\]'
        matches = re.finditer(pattern, output)
        
        for match in matches:
            entity_type, text = match.groups()
            start = original_text.find(text)
            if start != -1:
                entities.append({
                    "text": text,
                    "type": self.entity_types.get(entity_type, "OTHER"),
                    "start": start,
                    "end": start + len(text)
                })
        return entities

    def analyze(self, text: str, options: dict = None) -> dict:
        try:
            # Format the prompt according to model's training format
            prompt = f"### Instruction: Identify and classify named entities in the following text.\nText: {text}\n### Response:"
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True
            ).to(self.model.device)
            
            # Generate predictions
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.1,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
            
            # Decode the model output
            predicted_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the response part after "### Response:"
            response_start = predicted_text.find("### Response:")
            if response_start != -1:
                predicted_text = predicted_text[response_start + len("### Response:"):].strip()
            
            # Parse the output and get entities with positions
            entities = self._parse_model_output(predicted_text, text)
            
            # Format the final response
            analysis = {
                "text": text,
                "entities": entities
            }
            
            return analysis
            
        except Exception as e:
            raise Exception(f"Error in the NER analysis: {str(e)}")