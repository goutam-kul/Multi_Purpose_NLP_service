from pydantic import BaseModel
from typing import Optional, List


class TextInput(BaseModel):
    text: str
    task: str
    options: Optional[dict] = None

    class config:
        jason_schema_extra = {
            "example": {
                "text": "I love this product! It works perfectly.",
                "task": "sentiment_analysis",
                "options": {"return_all_scores": True}
            }
        }