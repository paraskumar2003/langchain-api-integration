from fastapi import APIRouter, HTTPException
from ..models.index import ChatRequest, TodayResponse
from ..service.index import get_today_summary, get_question_evaluation, get_department_recommendation
from ..models.index import EvaluateQuestionRequest, DepartmentAssessmentRequest

router = APIRouter()

@router.post("/chat", response_model=TodayResponse)
async def chat(req: ChatRequest):
    """POST endpoint for GPT-based structured response."""
    result = get_today_summary(req.prompt)
    return result


@router.post("/question", response_model=dict)
async def evaluate_question(req: EvaluateQuestionRequest):

    """
    POST endpoint for evaluating a question and user response.

    Expected payload format:
    {
        "question": {
            "dimension": "visual",
            "level": "basic",
            "type": "written",
            "prompt_html": "Look at this 4-bar melody in C major. Count how many notes move by step (not skip).",
            "image_url": "https://storage.googleapis.com/mtnp-assets/visual/q21.png",
            "audio_url": null,
            "options": null,
            "response_type": "text",
            "response_file_url": "https://storage.googleapis.com/mtnp-assets/visual/q21.png",
            "response_text": "6"
        }
    }
    """
    question = req.question

    if not question:
        raise HTTPException(status_code=400, detail="Missing 'question' field in request body.")

    result = get_question_evaluation(question)
    # result = {"is_correct": True, "reason": "Correct answer!", "confidence": 1}
    return result

@router.post("/assessment/department", response_model=dict)
async def evaluate_department(req: DepartmentAssessmentRequest):
    """
    POST endpoint for evaluating the user's cognitive profile
    and identifying the most suitable corporate department.

    Expected payload format:
    {
        "cognitive_profile": {
            "visual": 8.2,
            "auditory": 4.1,
            "rhythmic": 5.3,
            "subconscious": 8.7,
            "confidence": 0.81
        }
    }
    """

    profile = req.cognitive_profile

    if not profile:
        raise HTTPException(
            status_code=400,
            detail="Missing 'cognitive_profile' in request body."
        )

    # Build ChatGPT prompt
    result = get_department_recommendation(profile.dict())

    return result



