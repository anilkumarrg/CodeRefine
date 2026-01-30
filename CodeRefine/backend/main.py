# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json

# -------------------------------
# 1️⃣ Create FastAPI app
# -------------------------------
app = FastAPI()

# -------------------------------
# 2️⃣ Enable CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow frontend to access
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# -------------------------------
# 3️⃣ Hugging Face configuration
# -------------------------------
HF_API_URL = "https://api-inference.huggingface.co/models/Salesforce/codegen-350M-mono"
HF_API_TOKEN = "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"  # <-- REPLACE WITH YOUR TOKEN
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# -------------------------------
# 4️⃣ Request model
# -------------------------------
class CodeRequest(BaseModel):
    language: str
    code: str

# -------------------------------
# 5️⃣ Root endpoint
# -------------------------------
@app.get("/")
def read_root():
    return {"message": "CodeRefine backend is running!"}

# -------------------------------
# 6️⃣ Review endpoint
# -------------------------------
@app.post("/review")
def review_code(request: CodeRequest):
    prompt = f"""
Analyze this {request.language} code and return a JSON with:
- bugs (list of strings)
- performance_issues (list of strings)
- best_practices (list of strings)
- optimized_code (string)

Here is the code:
{request.code}

Output JSON ONLY.
"""
    try:
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt})
    except Exception as e:
        return {
            "bugs": ["Error calling AI"],
            "performance_issues": ["Error calling AI"],
            "best_practices": ["Error calling AI"],
            "optimized_code": str(e)
        }

    if response.status_code != 200:
        return {
            "bugs": ["Error calling AI"],
            "performance_issues": ["Error calling AI"],
            "best_practices": ["Error calling AI"],
            "optimized_code": f"Status code: {response.status_code}"
        }

    ai_output = response.json()
    result_text = ai_output[0].get("generated_text", "")

    # Try to parse AI JSON output
    try:
        data = json.loads(result_text)
        return {
            "bugs": data.get("bugs", []),
            "performance_issues": data.get("performance_issues", []),
            "best_practices": data.get("best_practices", []),
            "optimized_code": data.get("optimized_code", "")
        }
    except json.JSONDecodeError:
        # Fallback if AI output is not proper JSON
        return {
            "bugs": [],
            "performance_issues": [],
            "best_practices": [],
            "optimized_code": result_text
        }
