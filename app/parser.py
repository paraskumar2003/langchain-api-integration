import json
from langchain_core.output_parsers import BaseOutputParser

class JSONOutputParser(BaseOutputParser):
    """Ensures model returns valid JSON only."""

    def parse(self, text: str):
        text = text.strip()
        try:
            if text.startswith("```json"):
                text = text.removeprefix("```json").removesuffix("```").strip()
            return json.loads(text)
        except json.JSONDecodeError:
            raise ValueError(f"Model did not return valid JSON:\n{text}")
