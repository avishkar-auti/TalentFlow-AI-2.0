import os
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
        
        # Standard templates (0 tokens, Jinja2 only)
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
