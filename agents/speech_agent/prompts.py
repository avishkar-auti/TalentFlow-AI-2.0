"""Prompts for LLM interactions in Speech Agent."""

SPEECH_ANALYSIS_PROMPT = """
You are an expert communication and speech analyst for a recruitment platform.
Analyze the following interview transcript and provide a nuanced evaluation of the candidate's speech.

Candidate ID: {candidate_id}
Interview ID: {interview_id}

Deterministic Metrics Computed:
- Total Words: {word_count}
- Speaking Pace: {speaking_pace} WPM
- Vocabulary Diversity: {vocab_diversity} (Type-Token Ratio)
- Total Filler Words: {total_fillers}
- Fillers Per Minute: {fillers_per_minute}

Interview Transcript:
{transcript}

Based on the transcript and the provided metrics, evaluate the following on a scale of 0 to 100:
1. Communication Clarity: How clearly does the candidate convey their thoughts?
2. Confidence: Does the candidate sound sure of themselves and their answers?
3. Articulation: Are ideas expressed articulately and coherently?
4. Overall Fluency: Considering the pace, fillers, and flow, how fluent is the speech?

Return the results in a JSON format matching the following structure exactly, with no additional text:
{{
    "communication_clarity_score": <int>,
    "confidence_score": <int>,
    "articulation_score": <int>,
    "overall_fluency_score": <int>,
    "feedback": "<A detailed qualitative feedback paragraph covering strengths and areas for improvement>"
}}
"""
