from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    prompt: str

    

class TodayResponse(BaseModel):
    date: str = Field(..., description="Today's date in YYYY-MM-DD format")
    festivals: list[str] = Field(..., description="List of festivals celebrated today")
    summary: str = Field(..., description="Brief summary or note about today")
