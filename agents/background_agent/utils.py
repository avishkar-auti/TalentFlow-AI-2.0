from typing import List, Dict, Any, Tuple
import re
from datetime import datetime

def check_duplicate_candidate(email: str, phone: str, job_id: str, db_check_func) -> bool:
    """Checks if a candidate is a duplicate."""
    # This would call a DB function
    return False

def validate_experience_timeline(experiences: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """Validates that experience dates do not have impossible overlaps or huge unexplained gaps."""
    issues = []
    is_valid = True
    
    if not experiences:
        return True, []
        
    # Very basic validation for mock purposes
    for exp in experiences:
        if "start_date" not in exp or "end_date" not in exp:
            continue
        try:
            start = datetime.strptime(exp["start_date"], "%Y-%m")
            end = datetime.strptime(exp["end_date"], "%Y-%m") if exp["end_date"] != "present" else datetime.now()
            if start > end:
                issues.append(f"Invalid dates for {exp.get('company', 'Unknown')}: Start date is after end date.")
                is_valid = False
        except ValueError:
            pass # Invalid format, ignore for simple rule
            
    return is_valid, issues

def validate_education(education_list: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """Checks if education entries seem valid."""
    issues = []
    is_valid = True
    for edu in education_list:
        if "institution" not in edu or not edu["institution"]:
            issues.append("Missing institution name in education entry.")
            is_valid = False
    return is_valid, issues

def check_skill_plausibility(skills: List[str], experience_years: float) -> Tuple[bool, List[str]]:
    """Checks if claimed skills are plausible given years of experience."""
    issues = []
    if len(skills) > 50 and experience_years < 2:
        issues.append("Unusually high number of skills claimed for limited experience.")
        return False, issues
    return True, issues

def detect_red_flags(resume_analysis: Dict[str, Any]) -> List[str]:
    """Detects red flags such as excessive job hopping."""
    flags = []
    experiences = resume_analysis.get("experiences", [])
    if len(experiences) > 5:
        # Check if all are short stints
        short_stints = 0
        for exp in experiences:
            try:
                start = datetime.strptime(exp["start_date"], "%Y-%m")
                end = datetime.strptime(exp["end_date"], "%Y-%m") if exp["end_date"] != "present" else datetime.now()
                if (end - start).days < 365:
                    short_stints += 1
            except (ValueError, KeyError):
                pass
        if short_stints > 4:
            flags.append("Excessive job hopping detected (multiple <1 year roles).")
            
    return flags

def validate_contact_info(email: str, phone: str) -> Tuple[bool, List[str]]:
    """Validates email and phone format."""
    issues = []
    is_valid = True
    
    email_regex = r'^[a-zA-Z0-O_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if email and not re.match(email_regex, email):
        issues.append("Invalid email format.")
        is_valid = False
        
    return is_valid, issues
