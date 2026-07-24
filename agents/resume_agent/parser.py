"""
Resume Structure Parser using Groq Structured Output & Rule-based AST Extraction.
"""
import re
import json
import logging
from typing import Dict, Any, List
from backend.tools import llm_tools
from .prompts import RESUME_PARSING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class ResumeParser:
    """Parses raw text and AST blocks into structured domain JSON."""

    @staticmethod
    async def parse_resume_content(raw_text: str, blocks_ast: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parses text content using LLM (Groq) with robust rule-based AST fallback.
        """
        # Try parsing via Groq LLM tool first
        try:
            response_json_str = await llm_tools.groq_complete(
                prompt=f"Resume Content:\n{raw_text[:6000]}",
                system_prompt=RESUME_PARSING_SYSTEM_PROMPT,
                response_format="json_object",
                model="llama-3.3-70b-versatile"
            )
            parsed_data = json.loads(response_json_str)
            logger.info("Successfully parsed resume using Groq structured LLM.")
            return parsed_data
        except Exception as e:
            logger.warning(f"Groq LLM parsing unavailable or failed ({e}). Executing AST rule-based parser fallback.")
            return ResumeParser._fallback_rule_based_parser(raw_text, blocks_ast)

    @staticmethod
    def _fallback_rule_based_parser(text: str, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Rule-based regex and AST layout parser fallback when LLM is offline/unconfigured."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # 1. Extract contact info
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)

        # 2. Extract technical skills via common keyword dictionary
        common_tech_stack = [
            "Python", "FastAPI", "React", "TypeScript", "JavaScript", "Docker", 
            "Kubernetes", "AWS", "Firebase", "Firestore", "SQL", "PostgreSQL", 
            "MongoDB", "OpenCV", "MediaPipe", "Git", "REST API", "GraphQL", 
            "Node.js", "Express", "Tailwind CSS", "C++", "Java", "PyTorch", "TensorFlow"
        ]
        
        extracted_skills = []
        text_lower = text.lower()
        for tech in common_tech_stack:
            if re.search(r'\b' + re.escape(tech.lower()) + r'\b', text_lower):
                extracted_skills.append({"name": tech, "category": "Technical", "level": "Proficient"})

        # 3. Extract Companies & Experience hints.
        # Shapes must match the Experience pydantic model: company, title, description (List[str]).
        experience_list = []
        companies = []
        for line in lines:
            if any(term in line.lower() for term in ["inc", "llc", "corp", "ltd", "technologies", "solutions", "software"]):
                if len(line) < 60:
                    companies.append(line)
                    experience_list.append({
                        "company": line,
                        "title": "Software Engineer",
                        "description": [line],
                    })

        # 4. Extract Education — shape must match the Education model: institution, degree.
        education_list = []
        for line in lines:
            if any(degree in line.lower() for degree in ["bachelor", "master", "phd", "b.s", "m.s", "b.tech", "m.tech", "university", "college"]):
                education_list.append({
                    "degree": line,
                    "institution": line,
                })

        return {
            "parsedText": text[:1500],
            "summary": text[:400],
            "email": emails[0] if emails else "",
            "phone": phones[0] if phones else "",
            "skills": extracted_skills,
            "education": education_list if education_list else [{"degree": "Bachelor of Science", "institution": "University"}],
            # experience must be a list of Experience-shaped dicts, not a summary string.
            "experience": experience_list,
            "companies": list(set(companies)),
            # projects must match the Project model: name, description, technologies.
            "projects": [],
            "certifications": [],
            "missingKeywords": []
        }
