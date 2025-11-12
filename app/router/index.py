from fastapi import APIRouter
from ..models.index import ChatRequest, TodayResponse
from ..service.index import get_today_summary

router = APIRouter()

@router.post("/chat", response_model=TodayResponse)
async def chat(req: ChatRequest):
    """POST endpoint for GPT-based structured response."""
    result = get_today_summary(req.prompt)
    return result


@router.post("/question")
async def evaluate_question(req: dict):
    """
    POST endpoint for evaluating a question and user response.

    Expected payload format:
    {
        "question": {
            "dimension": "visual",
            "level": "basic",
            "type": "written",
            "prompt_html": "...",
            "response_type": "text",
            "response_text": "..."
        }
    }
    """
    question = req.get("question")

    if not question:
        raise HTTPException(status_code=400, detail="Missing 'question' field in request body.")

    result = get_question_evaluation(question)
    return result


