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
You are an expert evaluator for a music theory and visual reasoning exam.

{user_response_section}

QUESTION DETAILS:
-----------------
{question_json}

EVALUATION DIMENSIONS:
---------------------
In addition to correctness, evaluate the user's response on the following four cognitive dimensions.
Each dimension must be scored STRICTLY from 1 to 10.

1. VISUAL (1–10)
- Measures visual understanding, imagery, notation recognition, diagrams, shapes, symbols, or spatial reasoning.
- 1 = No visual understanding
- 10 = Strong visual or symbolic comprehension

2. AUDITORY (1–10)
- Measures understanding based on sound, tone, pitch, listening, melody, harmony, or audio perception.
- 1 = No auditory understanding
- 10 = Excellent auditory reasoning

3. RHYTHMIC (1–10)
- Measures timing, rhythm, tempo, beats, meter, or pattern recognition in music.
- 1 = No rhythmic awareness
- 10 = Strong rhythmic precision

4. SUBCONSCIOUS (1–10)
- Measures intuitive grasp, instinctive correctness, conceptual clarity without explicit explanation.
- 1 = Guesswork or confusion
- 10 = Clear intuitive mastery

SCORING RULES:
- Scores must be integers between 1 and 10.
- Do NOT return values outside this range.
- If a dimension cannot be inferred, return a low but non-zero score (e.g., 3–4).


EVALUATION RULES:
1. If response_type == "text": evaluate only using the text above.
2. If response_type != "text": evaluate using the file above.
3. Compare the user response to the expected correct concept.

CONFIDENCE SCORE RULE:
The confidence score must be a float from 0 to 1.

It represents how certain you are about your evaluation based on:
- clarity of the user response
- match to the expected concept
- completeness of reasoning
- absence of ambiguity


RETURN STRICT JSON ONLY IN THIS FORMAT:
{{
  "confidence": 0.75,
  "is_correct": true,
  "reason": "explanation",
  "visual": 1,
  "auditory": 1,
  "rhythmic": 1,
  "subconscious": 1
}}

Do not include markdown, comments, or extra text. Output JSON only.

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

    visual = clamp_score(parsed.get("visual"))
    auditory = clamp_score(parsed.get("auditory"))
    rhythmic = clamp_score(parsed.get("rhythmic"))
    subconscious = clamp_score(parsed.get("subconscious"))

    if not isinstance(confidence, int) or not (0 <= confidence <= 1):
        confidence = 0.5

    if not isinstance(is_correct, bool):
        is_correct = False

    if not isinstance(reason, str):
        reason = "Model returned invalid reason."

    return {
        "confidence": float(confidence),
        "is_correct": is_correct,
        "reason": reason,
        "visual": visual,
        "auditory": auditory,
        "rhythmic": rhythmic,
        "subconscious": subconscious
    }
