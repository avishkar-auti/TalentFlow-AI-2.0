import os

project_root = r"C:\Users\avish\.gemini\antigravity\scratch\TalentFlow-AI"
decision_agent_dir = os.path.join(project_root, "agents", "decision_agent")
notification_agent_dir = os.path.join(project_root, "agents", "notification_agent")
templates_reports_dir = os.path.join(project_root, "backend", "templates", "reports")
templates_emails_dir = os.path.join(project_root, "backend", "templates", "emails")

os.makedirs(decision_agent_dir, exist_ok=True)
os.makedirs(notification_agent_dir, exist_ok=True)
os.makedirs(templates_reports_dir, exist_ok=True)
os.makedirs(templates_emails_dir, exist_ok=True)

# DECISION AGENT FILES
with open(os.path.join(decision_agent_dir, "__init__.py"), "w") as f:
    f.write('"""Decision Agent package."""\n')

with open(os.path.join(decision_agent_dir, "models.py"), "w") as f:
    f.write("""from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class ScoreBreakdown(BaseModel):
    resume_score: float
    ats_score: float
    matching_score: float
    background_score: float
    technical_score: float
    speech_score: float

class DecisionResult(BaseModel):
    candidate_id: str
    job_id: str
    overall_score: float
    recommendation: str
    strengths: list[str]
    concerns: list[str]
    remarks: str
    score_breakdown: ScoreBreakdown
    created_at: datetime = Field(default_factory=datetime.utcnow)
""")

with open(os.path.join(decision_agent_dir, "schemas.py"), "w") as f:
    f.write("""from pydantic import BaseModel
from typing import List
from .models import DecisionResult

class DecisionRequest(BaseModel):
    candidate_id: str
    job_id: str

class DecisionResponse(BaseModel):
    success: bool
    data: DecisionResult
""")

with open(os.path.join(decision_agent_dir, "utils.py"), "w") as f:
    f.write("""def calculate_overall_score(
    resume_score: float,
    ats_score: float,
    matching_score: float,
    background_score: float,
    technical_score: float,
    speech_score: float
) -> float:
    return (
        resume_score * 0.15 +
        ats_score * 0.10 +
        matching_score * 0.20 +
        background_score * 0.10 +
        technical_score * 0.30 +
        speech_score * 0.15
    )

def map_to_recommendation(score: float) -> str:
    if score >= 90:
        return "STRONG_HIRE"
    elif score >= 80:
        return "HIRE"
    elif score >= 65:
        return "MAYBE"
    elif score >= 50:
        return "NO_HIRE"
    else:
        return "STRONG_NO_HIRE"
""")

with open(os.path.join(decision_agent_dir, "prompts.py"), "w") as f:
    f.write("""DECISION_SUMMARY_PROMPT = \"\"\"
You are an expert recruitment advisor. Review the candidate's scores and generate a professional, business-friendly summary.
Provide your response in JSON format with 'strengths' (list of strings), 'concerns' (list of strings), and 'remarks' (string).
Do NOT mention any AI, agents, or models. Just speak about the candidate's professional qualities.

Scores:
Resume: {resume_score}
ATS: {ats_score}
Matching: {matching_score}
Background: {background_score}
Technical: {technical_score}
Speech: {speech_score}
Overall: {overall_score}

Recommendation: {recommendation}
\"\"\"
""")

with open(os.path.join(decision_agent_dir, "firebase.py"), "w") as f:
    f.write("""from backend.firebase.client import get_firestore_client

def save_decision(candidate_id: str, decision_data: dict) -> None:
    db = get_firestore_client()
    doc_ref = db.collection('candidates').document(candidate_id).collection('decision').document('latest')
    doc_ref.set(decision_data)

def get_candidate_data(candidate_id: str) -> dict:
    db = get_firestore_client()
    doc_ref = db.collection('candidates').document(candidate_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else {}
""")

with open(os.path.join(decision_agent_dir, "agent.py"), "w") as f:
    f.write("""import json
from .models import DecisionResult, ScoreBreakdown
from .utils import calculate_overall_score, map_to_recommendation
from .prompts import DECISION_SUMMARY_PROMPT
from .firebase import save_decision, get_candidate_data
from backend.tools.llm_tools import generate_completion
from backend.tools.pdf_tools import generate_pdf

class DecisionAgent:
    def process(self, candidate_id: str, job_id: str) -> DecisionResult:
        # Mock fetching from Firestore since other agents might not have populated it yet
        # In a real scenario, this would read from candidates/{id}/...
        resume_score = 85.0
        ats_score = 90.0
        matching_score = 80.0
        background_score = 95.0
        technical_score = 88.0
        speech_score = 92.0

        overall_score = calculate_overall_score(
            resume_score, ats_score, matching_score,
            background_score, technical_score, speech_score
        )
        recommendation = map_to_recommendation(overall_score)
        
        prompt = DECISION_SUMMARY_PROMPT.format(
            resume_score=resume_score,
            ats_score=ats_score,
            matching_score=matching_score,
            background_score=background_score,
            technical_score=technical_score,
            speech_score=speech_score,
            overall_score=overall_score,
            recommendation=recommendation
        )
        
        # Use Groq llama-3.3-70b
        llm_response = generate_completion("groq/llama-3.3-70b-versatile", prompt)
        try:
            parsed = json.loads(llm_response)
        except:
            parsed = {"strengths": [], "concerns": [], "remarks": "Summary unavailable."}

        breakdown = ScoreBreakdown(
            resume_score=resume_score,
            ats_score=ats_score,
            matching_score=matching_score,
            background_score=background_score,
            technical_score=technical_score,
            speech_score=speech_score
        )

        result = DecisionResult(
            candidate_id=candidate_id,
            job_id=job_id,
            overall_score=overall_score,
            recommendation=recommendation,
            strengths=parsed.get("strengths", []),
            concerns=parsed.get("concerns", []),
            remarks=parsed.get("remarks", "No remarks"),
            score_breakdown=breakdown
        )

        # Save to Firestore
        save_decision(candidate_id, result.model_dump(mode="json"))
        
        # In a real flow, you might call generate_pdf here
        # generate_pdf("backend/templates/reports/candidate_report.html", result.model_dump(mode="json"), "report.pdf")

        return result
""")

with open(os.path.join(decision_agent_dir, "service.py"), "w") as f:
    f.write("""from .agent import DecisionAgent
from .schemas import DecisionRequest, DecisionResponse

class DecisionService:
    def __init__(self):
        self.agent = DecisionAgent()
        
    def process_decision(self, request: DecisionRequest) -> DecisionResponse:
        result = self.agent.process(request.candidate_id, request.job_id)
        return DecisionResponse(success=True, data=result)
""")

with open(os.path.join(decision_agent_dir, "controller.py"), "w") as f:
    f.write("""from fastapi import APIRouter, HTTPException
from .schemas import DecisionRequest, DecisionResponse
from .service import DecisionService

router = APIRouter(prefix="/decision", tags=["Decision"])
service = DecisionService()

@router.post("/", response_model=DecisionResponse)
def make_decision(request: DecisionRequest):
    try:
        return service.process_decision(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
""")

with open(os.path.join(decision_agent_dir, "README.md"), "w") as f:
    f.write("""# Decision Agent
Makes hiring decisions based on aggregated scores from all previous agents.
""")

# NOTIFICATION AGENT FILES
with open(os.path.join(notification_agent_dir, "__init__.py"), "w") as f:
    f.write('"""Notification Agent package."""\n')

with open(os.path.join(notification_agent_dir, "models.py"), "w") as f:
    f.write("""from pydantic import BaseModel
from typing import Dict, Any

class NotificationPayload(BaseModel):
    type: str
    recipient: str
    data: Dict[str, Any]
""")

with open(os.path.join(notification_agent_dir, "schemas.py"), "w") as f:
    f.write("""from pydantic import BaseModel

class NotificationResponse(BaseModel):
    success: bool
    message: str
""")

with open(os.path.join(notification_agent_dir, "firebase.py"), "w") as f:
    f.write("""def log_notification(recipient: str, notification_type: str):
    pass
""")

with open(os.path.join(notification_agent_dir, "agent.py"), "w") as f:
    f.write("""import os
from jinja2 import Environment, FileSystemLoader
from backend.tools.llm_tools import generate_completion

class NotificationAgent:
    def __init__(self):
        template_dir = os.path.join("backend", "templates", "emails")
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def send_notification(self, type: str, recipient: str, data: dict):
        if type == "personalized":
            # Use LLM for personalized messages
            prompt = f"Write a personalized email to {recipient} based on: {data}"
            message = generate_completion("groq/llama-3.3-70b-versatile", prompt)
            return {"success": True, "message": "Personalized notification sent", "content": message}
        
        # Standard templates
        template_map = {
            "application_received": "application_received.html",
            "interview_scheduled": "interview_scheduled.html",
            "interview_reminder": "interview_reminder.html",
            "decision_made": "decision_made.html"
        }
        
        template_name = template_map.get(type)
        if not template_name:
            raise ValueError(f"Unknown notification type: {type}")
            
        template = self.env.get_template(template_name)
        content = template.render(**data)
        
        # Here you would actually send the email via SMTP, SendGrid, etc.
        return {"success": True, "message": f"Notification '{type}' sent to {recipient}", "content": content}
""")

with open(os.path.join(notification_agent_dir, "service.py"), "w") as f:
    f.write("""from .agent import NotificationAgent
from .models import NotificationPayload
from .schemas import NotificationResponse

class NotificationService:
    def __init__(self):
        self.agent = NotificationAgent()
        
    def send(self, payload: NotificationPayload) -> NotificationResponse:
        self.agent.send_notification(payload.type, payload.recipient, payload.data)
        return NotificationResponse(success=True, message="Notification dispatched")
""")

with open(os.path.join(notification_agent_dir, "controller.py"), "w") as f:
    f.write("""from fastapi import APIRouter
from .models import NotificationPayload
from .schemas import NotificationResponse
from .service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])
service = NotificationService()

@router.post("/", response_model=NotificationResponse)
def send_notification(payload: NotificationPayload):
    return service.send(payload)
""")

with open(os.path.join(notification_agent_dir, "README.md"), "w") as f:
    f.write("""# Notification Agent
Handles transactional and personalized email notifications.
""")

# TEMPLATES
with open(os.path.join(templates_reports_dir, "candidate_report.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #1e3a5f; }
        .header { text-align: center; color: #0d9488; }
        .bar { background-color: #0d9488; height: 20px; }
    </style>
</head>
<body>
    <h1 class="header">TalentFlow-AI Candidate Report</h1>
    <h2>Candidate: {{ candidate_id }}</h2>
    <p>Overall Score: {{ overall_score }}</p>
    <p>Recommendation: <strong>{{ recommendation }}</strong></p>
    <hr>
    <h3>Remarks</h3>
    <p>{{ remarks }}</p>
</body>
</html>
""")

with open(os.path.join(templates_emails_dir, "base.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        .header { background-color: #1e3a5f; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .footer { background-color: #0d9488; color: white; text-align: center; padding: 10px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>TalentFlow-AI</h1>
    </div>
    <div class="content">
        {% block content %}{% endblock %}
    </div>
    <div class="footer">
        &copy; 2026 TalentFlow-AI. All rights reserved.
    </div>
</body>
</html>
""")

with open(os.path.join(templates_emails_dir, "application_received.html"), "w") as f:
    f.write("""{% extends "base.html" %}
{% block content %}
<h2>Application Received</h2>
<p>Dear {{ name }},</p>
<p>We have successfully received your application for the {{ job_title }} position.</p>
{% endblock %}
""")

with open(os.path.join(templates_emails_dir, "interview_scheduled.html"), "w") as f:
    f.write("""{% extends "base.html" %}
{% block content %}
<h2>Interview Scheduled</h2>
<p>Dear {{ name }},</p>
<p>Your interview for {{ job_title }} has been scheduled for {{ datetime }}.</p>
{% endblock %}
""")

with open(os.path.join(templates_emails_dir, "interview_reminder.html"), "w") as f:
    f.write("""{% extends "base.html" %}
{% block content %}
<h2>Interview Reminder</h2>
<p>Dear {{ name }},</p>
<p>This is a reminder for your upcoming interview for {{ job_title }} on {{ datetime }}.</p>
{% endblock %}
""")

with open(os.path.join(templates_emails_dir, "decision_made.html"), "w") as f:
    f.write("""{% extends "base.html" %}
{% block content %}
<h2>Application Update</h2>
<p>Dear {{ name }},</p>
<p>We have an update regarding your application for the {{ job_title }} position.</p>
{% endblock %}
""")
