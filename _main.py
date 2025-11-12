from fastapi import FastAPI
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import BaseOutputParser
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

app = FastAPI()

# Initialize GPT model
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Request DTO
class ChatRequest(BaseModel):
    prompt: str

# Strict JSON schema
class TodayResponse(BaseModel):
    date: str = Field(..., description="Today's date in YYYY-MM-DD format")
    festivals: list[str] = Field(..., description="List of festivals celebrated today")
    summary: str = Field(..., description="Brief summary or note about today")

# Custom parser to clean model response
class JSONOutputParser(BaseOutputParser):
    def parse(self, text: str):
        text = text.strip()
        try:
            if text.startswith("```json"):
                text = text.strip("```json").strip("```").strip()
            return json.loads(text)
        except json.JSONDecodeError:
            raise ValueError(f"Model did not return valid JSON:\n{text}")

@app.post("/chat")
async def chat(req: ChatRequest):
    today = datetime.now().strftime("%Y-%m-%d")
    system_prompt = f"""
You are a strict JSON generator. 
Return ONLY a valid JSON object in this format:
{{
  "date": "YYYY-MM-DD",
  "festivals": ["festival_name_1", "festival_name_2"],
  "summary": "short sentence about today"
}}

Today's date is {today}. 
User prompt: {req.prompt}
"""

    response = model.invoke(system_prompt)
    parser = JSONOutputParser()
    parsed = parser.parse(response.content)
    return parsed
