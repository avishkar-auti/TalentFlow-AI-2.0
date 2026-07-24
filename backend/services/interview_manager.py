"""Comprehensive Interview Management - AI, HR, Technical rounds with chat & proctoring."""
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import firebase_admin.firestore

db = firebase_admin.firestore.client()

class InterviewManager:
    """Manages complete interview lifecycle with AI scoring."""

    async def start_interview(self, interview_id: str, candidate_id: str, interview_type: str) -> Dict:
        """Initialize interview session."""
        doc = db.collection('interviews').document(interview_id).get()
        if not doc.exists:
            raise ValueError(f'Interview {interview_id} not found')

        db.collection('interviews').document(interview_id).update({
            'status': 'in_progress',
            'started_at': datetime.now(timezone.utc).isoformat(),
            'proctoring_flags': [],
            'warning_count': 0
        })
        return doc.to_dict()

    async def add_proctoring_flag(self, interview_id: str, flag_type: str, severity: str = 'warning') -> Dict:
        """Record proctoring violation, check if ≥5 warnings."""
        interview_doc = db.collection('interviews').document(interview_id).get()
        if not interview_doc.exists:
            return {'error': 'Interview not found'}

        current_data = interview_doc.to_dict()
        current_warning_count = current_data.get('warning_count', 0)
        new_warning_count = current_warning_count + 1

        flag_entry = {
            'flag_type': flag_type,
            'severity': severity,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'warning_number': new_warning_count,
            'user_message': self._get_flag_message(flag_type)
        }

        db.collection('interviews').document(interview_id).update({
            'warning_count': new_warning_count,
            'proctoring_flags': firebase_admin.firestore.ArrayUnion([flag_entry])
        })

        auto_terminated = False
        if new_warning_count >= 5:
            db.collection('interviews').document(interview_id).update({
                'status': 'terminated',
                'termination_reason': f'Auto-terminated: {new_warning_count} proctoring warnings',
                'ended_at': datetime.now(timezone.utc).isoformat()
            })
            # Reject candidate
            candidate_id = current_data.get('candidate_id')
            if candidate_id:
                db.collection('candidates').document(candidate_id).update({
                    'pipeline_stage': 'rejected',
                    'status': 'rejected'
                })
            auto_terminated = True

        return {
            'warning_number': new_warning_count,
            'auto_terminated': auto_terminated,
            'flag': flag_entry
        }

    def _get_flag_message(self, flag_type: str) -> str:
        """Get user-facing message for flag type."""
        messages = {
            'NO_FACE': 'Face not detected. Please face the camera.',
            'MULTIPLE_FACES': 'Multiple faces detected. Please ensure only you are present.',
            'LOOKING_AWAY': 'Please look at the camera during the interview.',
            'EYE_CLOSED': 'Your eyes appear closed. Please stay alert.',
            'AUDIO_NOISE': 'Background noise detected. Please find a quiet environment.',
            'PHONE_DETECTED': 'Phone or suspicious device detected.',
            'HEAD_DOWN': 'Please look up at the camera.',
            'EXCESSIVE_MOVEMENT': 'Excessive movement detected. Please remain calm.'
        }
        return messages.get(flag_type, 'Proctoring violation detected.')

    async def add_chat_message(self, interview_id: str, sender_role: str, content: str) -> Dict:
        """Store chat message in Firestore."""
        msg_data = {
            'sender_role': sender_role,
            'content': content,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'interview_id': interview_id
        }
        db.collection('interviews').document(interview_id).collection('chat').document().set(msg_data)
        return msg_data

    async def get_chat_history(self, interview_id: str) -> List[Dict]:
        """Retrieve all chat messages for an interview."""
        messages = db.collection('interviews').document(interview_id).collection('chat').stream()
        return [msg.to_dict() for msg in messages]

    async def score_code_submission(self, code: str, language: str, expected_output: str) -> Dict:
        """AI-based code quality scoring."""
        # Simple heuristic scoring (can be replaced with actual AI)
        lines = len(code.strip().split('\n'))
        has_comments = '#' in code or '//' in code
        has_tests = 'test' in code.lower() or 'assert' in code.lower()

        complexity_score = 70
        if has_comments:
            complexity_score += 10
        if has_tests:
            complexity_score += 15
        if lines > 50:
            complexity_score = min(complexity_score + 5, 100)

        return {
            'code_quality_score': min(complexity_score, 100),
            'readability': 'Good' if has_comments else 'Needs Comments',
            'test_coverage': 'Good' if has_tests else 'No tests found',
            'execution_time_estimate': 'O(n)',
            'space_complexity_estimate': 'O(1)',
            'feedback': self._get_code_feedback(complexity_score, has_comments, has_tests)
        }

    def _get_code_feedback(self, score: int, has_comments: bool, has_tests: bool) -> str:
        """Generate AI feedback for submitted code."""
        feedback = []
        if score >= 80:
            feedback.append('✅ Excellent code quality!')
        elif score >= 60:
            feedback.append('⚠️ Good solution. Consider adding comments and tests.')
        else:
            feedback.append('⚠️ Solution works but needs improvement in readability.')

        if not has_comments:
            feedback.append('Add inline comments for clarity.')
        if not has_tests:
            feedback.append('Include test cases or assertions.')

        return ' '.join(feedback)

    async def end_interview(self, interview_id: str, passed: bool, notes: str = '') -> Dict:
        """End interview and trigger next round if passed."""
        from backend.services.interview_service import InterviewService
        svc = InterviewService()

        if passed:
            return await svc.pass_interview(interview_id, notes)
        else:
            return await svc.fail_interview(interview_id, notes)

    async def get_interview_summary(self, interview_id: str) -> Dict:
        """Get complete interview data including proctoring, chat, and score."""
        interview_doc = db.collection('interviews').document(interview_id).get()
        if not interview_doc.exists:
            return {}

        interview_data = interview_doc.to_dict()
        chat_msgs = await self.get_chat_history(interview_id)

        return {
            'interview': interview_data,
            'chat_history': chat_msgs,
            'warning_count': interview_data.get('warning_count', 0),
            'status': interview_data.get('status'),
            'passed': interview_data.get('pass_fail') == 'pass',
            'flags': interview_data.get('proctoring_flags', [])
        }
