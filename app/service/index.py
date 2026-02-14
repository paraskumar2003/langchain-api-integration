import os
import json
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

def clamp_score(value):
    if isinstance(value, int) and 1 <= value <= 10:
        return value
    return 5  # safe neutral fallback


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
    response_type = question.response_type
    response_text = question.response_text
    response_file_url = question.response_file_url


    question_json = json.dumps(
    question.model_dump(mode="json"),
    ensure_ascii=False,
    indent=2)


    print(question_json)


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
You are an expert evaluator for MTNP, which produces long-form HR interpretation reports 
based on how users visually interpret structured information. This is not a scoring system, 
personality test, musical test, or psychometric questionnaire.

{user_response_section}

QUESTION DETAILS:
-----------------
{question_json}

TASK:
-----
Evaluate the user's response and provide:
1. Correctness assessment (is_correct: true/false)
2. Brief explanation (reason)
3. Confidence score (0 to 1)
4. HR analysis (approach, strengths, omissions, workplace interpretation)

RETURN STRICT JSON ONLY IN THIS FORMAT:
{{
  "confidence": 0.75,
  "is_correct": true,
  "reason": "brief explanation",
  "candidates_approach": "how they approached the material",
  "demonstrated_strengths": "what they did well",
  "omissions_or_delays": "what they missed or delayed",
  "hr_interpretation": "workplace implications"
}}

Output JSON only. No markdown, no comments.
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

    # Set static cognitive dimension scores (not computed by GPT)
    visual = 1
    auditory = 1
    rhythmic = 1
    subconscious = 1

    # Extract new HR analysis fields
    candidates_approach = parsed.get("candidates_approach")
    demonstrated_strengths = parsed.get("demonstrated_strengths")
    omissions_or_delays = parsed.get("omissions_or_delays")
    hr_interpretation = parsed.get("hr_interpretation")

    if not isinstance(confidence, int) or not (0 <= confidence <= 1):
        confidence = 0.5

    if not isinstance(is_correct, bool):
        is_correct = False

    if not isinstance(reason, str):
        reason = "Model returned invalid reason."

    # Validate HR analysis fields
    if not isinstance(candidates_approach, str):
        candidates_approach = "No approach analysis available."

    if not isinstance(demonstrated_strengths, str):
        demonstrated_strengths = "No strengths analysis available."

    if not isinstance(omissions_or_delays, str):
        omissions_or_delays = "No omissions analysis available."

    if not isinstance(hr_interpretation, str):
        hr_interpretation = "No HR interpretation available."

    return {
        "confidence": float(confidence),
        "is_correct": is_correct,
        "reason": reason,
        "visual": visual,
        "auditory": auditory,
        "rhythmic": rhythmic,
        "subconscious": subconscious,
        "candidates_approach": candidates_approach,
        "demonstrated_strengths": demonstrated_strengths,
        "omissions_or_delays": omissions_or_delays,
        "hr_interpretation": hr_interpretation
    }

def get_department_recommendation(cognitive_profile: dict):
    profile_json = json.dumps(
        cognitive_profile,
        ensure_ascii=False,
        indent=2
    )

    system_prompt = f"""
You are an expert corporate psychologist and talent assessment specialist.

Based on the following cognitive profile derived from 15 evaluation questions,
identify the MOST SUITABLE corporate department for this user.

COGNITIVE PROFILE:
------------------
{profile_json}

Available departments:
- Software Engineering
- Data & Analytics
- Product Management
- UI/UX Design
- Marketing & Branding
- Sales & Business Development
- Operations
- HR & People Operations
- Finance

Rules:
- Choose ONE primary department.
- Optionally suggest one secondary department.
- Explain reasoning clearly.
- Then generate 8–10 relevant HR interview questions
  tailored specifically for the selected department.

RETURN STRICT JSON ONLY IN THIS FORMAT:
{{
  "primary_department": "",
  "secondary_department": "",
  "reasoning": "",
  "hr_questions": []
}}

Do not include markdown, comments, or extra text.
Output JSON only.
"""

    # 🔹 Call LLM
    response = model.invoke(system_prompt)

    # 🔹 Parse JSON
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
                    parsed = json.loads(raw[start:end + 1])
                except:
                    parsed = {}
            else:
                parsed = {}

    # 🔹 Validate output
    primary_department = parsed.get("primary_department")
    secondary_department = parsed.get("secondary_department")
    reasoning = parsed.get("reasoning")
    hr_questions = parsed.get("hr_questions")

    if not isinstance(primary_department, str):
        primary_department = "Unknown"

    if not isinstance(secondary_department, str):
        secondary_department = ""

    if not isinstance(reasoning, str):
        reasoning = "Model returned insufficient reasoning."

    if not isinstance(hr_questions, list):
        hr_questions = []

    # keep only string questions
    hr_questions = [q for q in hr_questions if isinstance(q, str)]

    return {
        "primary_department": primary_department,
        "secondary_department": secondary_department,
        "reasoning": reasoning,
        "hr_questions": hr_questions
    }
