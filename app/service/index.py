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
    """
    Evaluates a question + user response using an LLM prompt.
    Returns a dict with keys: confidence_score, is_correct, reason.
    """

    # 🧠 Step 1: Construct dynamic prompt with question data
    prompt = f"""
            {PROMPTS['evaluate_question']}

            Below is the question object. 
            If 'response_type' is "text", evaluate based on 'response_text'. 
            If 'response_type' is "image" or "audio", evaluate based on 'response_file_url'.

            Question Data:
            {json.dumps(question, ensure_ascii=False, indent=2)}
            """

    # 🧩 Step 2: Invoke the model
    try:
        print(prompt)
        # response = model.invoke(prompt)
        dummy_json = {
            "confidence_score": 0.85,
            "is_correct": True,
            "reason": "The user's answer correctly identifies the number of steps in the melody."
        }

        # Simulate the structure of an actual model response
        class DummyResponse:
            def __init__(self, content):
                self.content = content


        response = DummyResponse(content=json.dumps(dummy_json))        

        # 🧾 Step 3: Parse using JSONOutputParser
        parser = JSONOutputParser()

        try:
            evaluation = parser.parse(response.content)
        except Exception:
            # fallback to manual extraction if malformed JSON
            raw = response.content.strip()
            start, end = raw.find("{"), raw.rfind("}")
            if start != -1 and end != -1:
                try:
                    evaluation = json.loads(raw[start:end+1])
                except Exception:
                    evaluation = {}
            else:
                evaluation = {}

        # 🧱 Step 4: Validate structure
        if not isinstance(evaluation, dict):
            evaluation = {}

        evaluation.setdefault("confidence_score", 0.0)
        evaluation.setdefault("is_correct", False)
        evaluation.setdefault("reason", "Model returned invalid or incomplete response.")

        return evaluation

    except Exception as e:
        # 🧨 Catch model invocation errors
        return {
            "confidence_score": 0.0,
            "is_correct": False,
            "reason": f"Evaluation failed: {str(e)}"
        }
