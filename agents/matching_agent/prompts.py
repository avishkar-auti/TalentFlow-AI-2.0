ROLE_FIT_JUDGMENT_PROMPT = """
You are an expert technical recruiter and hiring manager. 
A candidate is missing some exact required skills, but may have transferable skills or related technologies.

Candidate Skills: {candidate_skills}
Missing Required Skills: {missing_skills}
Job Title: {job_title}
Job Description: {job_description}

Please evaluate if the candidate's existing skills can substitute for the missing skills.
Respond ONLY in valid JSON format.

Expected JSON schema:
{{
    "adjusted_skill_score": int, // A score from 0 to 100 based on transferable skills covering the gap. 0 means no coverage, 100 means full coverage.
    "reasoning": str, // Brief explanation of the evaluation
    "transferable_skills": [str] // List of candidate's skills that are transferable to the missing skills
}}
"""
