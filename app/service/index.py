import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from ..parser import JSONOutputParser
from ..prompts.index import PROMPTS

load_dotenv()

# Initialize GPT model once
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

def get_today_summary(prompt: str):
    """Handles GPT interaction and JSON parsing."""
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
User prompt: {prompt}
"""

    response = model.invoke(system_prompt)
    parser = JSONOutputParser()
    return parser.parse(response.content)

def get_question_evaluation(question: dict):
    response_type = question.get("response_type")
    response_text = question.get("response_text")
    response_file_url = question.get("response_file_url")

    if response_type == "text":
        user_response_section = f"""
USER RESPONSE (TEXT):
---------------------
{response_text}
"""
    else:
        user_response_section = f"""
USER RESPONSE (FILE):
---------------------
The user has submitted a file for evaluation: {response_file_url}
(This may be an image or audio file.)
"""

    # Build prompt with dynamic injected section
    system_prompt = f"""
You are an expert evaluator for a music theory and visual reasoning exam.

{user_response_section}

QUESTION DETAILS:
-----------------
{json.dumps(question, ensure_ascii=False, indent=2)}

EVALUATION RULES:
1. If response_type == "text": evaluate only using the text above.
2. If response_type != "text": evaluate using the file above.
3. Compare the user response to the expected correct concept.
4. Return STRICT JSON ONLY:

{{
  "confidence": 0.0,
  "is_correct": true,
  "reason": "explanation"
}}
"""

    # Call model
    response = model.invoke(system_prompt)

    # Parse JSON
    parser = JSONOutputParser()
    try:
        parsed = parser.parse(response.content)
    except:
        raw = response.content.strip()
        try:
            parsed = json.loads(raw)
        except:
            start, end = raw.find("{"), raw.rfind("}")
            if start != -1 and end != -1:
                try:
                    parsed = json.loads(raw[start:end+1])
                except:
                    parsed = {}
            else:
                parsed = {}

    # Validate output
    confidence = parsed.get("confidence")
    is_correct = parsed.get("is_correct")
    reason = parsed.get("reason")

    if not isinstance(confidence, (int, float)) or not (0 < confidence < 1):
        confidence = 0.5

    if not isinstance(is_correct, bool):
        is_correct = False

    if not isinstance(reason, str):
        reason = "Model returned invalid reason."

    return {
        "confidence": float(confidence),
        "is_correct": is_correct,
        "reason": reason
    }
