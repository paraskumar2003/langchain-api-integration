# FastAPI GPT Evaluation Service

A **FastAPI-based backend service** that uses **OpenAI (via LangChain)** to generate structured responses and evaluate user-submitted answers for music theory and visual reasoning questions.

This project exposes REST APIs for:

- Generating a **daily summary** in strict JSON format
- Evaluating **text, image, or audio-based questions** using GPT

---

## 🚀 Features

- ⚡ Built with **FastAPI**
- 🤖 OpenAI integration via **LangChain**
- 📦 Strict JSON output parsing
- 🎼 Supports **music theory & visual reasoning** evaluations
- 🧠 Deterministic evaluation (temperature = 0)
- 🛡️ Robust fallback parsing for malformed model output
- 🔐 Environment-based API key configuration

---

## 🧱 Project Structure

```text
app/
├── api/
│   └── index.py            # API routes
├── models/
│   └── index.py            # Pydantic request/response models
├── service/
│   └── index.py            # GPT interaction & evaluation logic
├── prompts/
│   └── index.py            # Prompt templates
├── parser/
│   └── json_parser.py      # Strict JSON output parser
├── main.py                 # FastAPI app entry
└── .env
```

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **FastAPI**
- **LangChain**
- **OpenAI API**
- **Pydantic**
- **dotenv**

---

## 🔑 Environment Setup

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 📦 Installation

```bash
git clone https://github.com/your-username/fastapi-gpt-evaluator.git
cd fastapi-gpt-evaluator

python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

---

## ▶️ Running the Server

```bash
uvicorn app.main:app --reload
```

Server will start at:

```
http://127.0.0.1:8000
```

Swagger docs:

```
http://127.0.0.1:8000/docs
```

---

## 📡 API Endpoints

---

### 🗓️ Generate Today’s Summary

```http
POST /chat
```

#### Request Body

```json
{
  "prompt": "Tell me about today's festivals in India"
}
```

#### Response

```json
{
  "date": "2025-12-19",
  "festivals": ["Festival A", "Festival B"],
  "summary": "Today is marked by cultural celebrations."
}
```

---

### 🧠 Evaluate Question Response

```http
POST /question
```

#### Request Body

```json
{
  "question": {
    "dimension": "visual",
    "level": "basic",
    "type": "written",
    "prompt_html": "Look at this 4-bar melody in C major. Count how many notes move by step.",
    "image_url": "https://example.com/image.png",
    "audio_url": null,
    "options": null,
    "response_type": "text",
    "response_text": "6",
    "response_file_url": null
  }
}
```

#### Response

```json
{
  "is_correct": true,
  "reason": "Correct answer!",
  "confidence": 0.95
}
```

---

## 🧠 Evaluation Logic

- **Text responses** are evaluated strictly using the submitted text
- **File-based responses** (image/audio) are evaluated using the provided URL
- Model output is required to be **strict JSON**
- Includes fallback parsing to handle malformed responses
- Confidence values are normalized between `0.0` and `1.0`

---

## 🛡️ Error Handling

- Missing `question` field → `400 Bad Request`
- Invalid model output → safe defaults applied
- JSON parsing failures handled gracefully

---

## 📈 Extensibility

This project is designed to be extended for:

- Multi-question evaluations
- Rubric-based scoring
- Confidence calibration
- Database persistence
- Authentication & rate limiting
- Async file ingestion (image/audio)

---

## 📄 License

MIT

---

## ⭐ Notes

- This service is **backend-only**
- Designed for **machine-to-machine** interaction
- Not intended to stream responses
- Uses deterministic GPT settings for evaluation consistency
