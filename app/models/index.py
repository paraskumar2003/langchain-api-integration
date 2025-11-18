from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    prompt: str

    

class TodayResponse(BaseModel):
    date: str = Field(..., description="Today's date in YYYY-MM-DD format")
    festivals: list[str] = Field(..., description="List of festivals celebrated today")
    summary: str = Field(..., description="Brief summary or note about today")


from pydantic import BaseModel, HttpUrl, field_validator, model_validator
from typing import Optional, List, Literal


class QuestionModel(BaseModel):
    dimension: Literal["visual", "aural", "theory"]
    level: Literal["basic", "intermediate", "advanced"]
    type: Literal["written", "mcq", "aural"]
    prompt_html: str

    image_url: Optional[HttpUrl] = None
    audio_url: Optional[HttpUrl] = None
    options: Optional[List[str]] = None

    response_type: Literal["text", "image", "audio"]

    response_text: Optional[str] = None
    response_file_url: Optional[HttpUrl] = None

    # ---------- Pydantic Conditional Validation (Joi-style) ----------
    @model_validator(mode="after")
    def validate_response(cls, values):
        rt = values.response_type

        if rt == "text":
            if not values.response_text:
                raise ValueError("response_text is required when response_type='text'")
        else:
            if not values.response_file_url:
                raise ValueError("response_file_url is required when response_type!='text'")

        return values


class EvaluateQuestionRequest(BaseModel):
    question: QuestionModel
