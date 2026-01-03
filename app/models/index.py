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
    dimension: Literal["visual", "auditory", "subconscious"]
    level: Literal["basic", "intermediate", "advanced"]
    type: Literal["written", "mcq", "audio", "psychometric", "image"]
    prompt_html: str

    image_url: Optional[HttpUrl] = None
    audio_url: Optional[HttpUrl] = None
    options: Optional[List[str]] = None

    response_type: Literal["text", "image", "audio", "mcq"]

    response_text: Optional[str] = None
    response_file_url: Optional[HttpUrl] = None

    # 🔹 Normalize empty string → None
    @field_validator("response_file_url", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    # 🔹 Conditional validation
    @model_validator(mode="after")
    def validate_response(cls, values):
        rt = values.response_type

        if rt == "text":
            if not values.response_text:
                raise ValueError(
                    "response_text is required when response_type='text'"
                )
        else:
            if not values.response_file_url:
                raise ValueError(
                    "response_file_url is required when response_type!='text'"
                )

        return values


class EvaluateQuestionRequest(BaseModel):
    question: QuestionModel
