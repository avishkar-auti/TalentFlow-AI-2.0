"""Real-time Activity Logger for Recruiter Dashboard"""
from datetime import datetime, timezone
import firebase_admin.firestore

db = firebase_admin.firestore.client()

class ActivityLogger:
    """Log and retrieve real hiring activities"""

    @staticmethod
    async def log_activity(action: str, candidate_id: str, details: dict = None) -> None:
        """Log an activity event"""
        activity = {
            'action': action,
            'candidate_id': candidate_id,
            'details': details or {},
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        db.collection('activity_logs').document().set(activity)

    @staticmethod
    async def get_recent_activities(limit: int = 10) -> list:
        """Get recent activities"""
        docs = db.collection('activity_logs').order_by('timestamp', direction='DESCENDING').limit(limit).stream()
        activities = []
        for doc in docs:
            data = doc.to_dict()
            # Get candidate name
            cand_doc = db.collection('candidates').document(data.get('candidate_id')).get()
            if cand_doc.exists:
                data['candidate_name'] = cand_doc.to_dict().get('name', 'Unknown')
            activities.append(data)
        return activities

    @staticmethod
    async def log_resume_upload(candidate_id: str, file_name: str, ats_score: float) -> None:
        """Log resume upload"""
        await ActivityLogger.log_activity(
            action='resume_uploaded',
            candidate_id=candidate_id,
            details={'file_name': file_name, 'ats_score': ats_score}
        )

    @staticmethod
    async def log_interview_scheduled(candidate_id: str, interview_type: str, scheduled_at: str) -> None:
        """Log interview scheduling"""
        await ActivityLogger.log_activity(
            action='interview_scheduled',
            candidate_id=candidate_id,
            details={'interview_type': interview_type, 'scheduled_at': scheduled_at}
        )

    @staticmethod
    async def log_stage_change(candidate_id: str, from_stage: str, to_stage: str) -> None:
        """Log pipeline stage change"""
        await ActivityLogger.log_activity(
            action='stage_changed',
            candidate_id=candidate_id,
            details={'from_stage': from_stage, 'to_stage': to_stage}
        )

    @staticmethod
    async def log_offer_sent(candidate_id: str, salary: str) -> None:
        """Log offer sent"""
        await ActivityLogger.log_activity(
            action='offer_sent',
            candidate_id=candidate_id,
            details={'salary': salary}
        )

    @staticmethod
    async def log_offer_accepted(candidate_id: str) -> None:
        """Log offer accepted"""
        await ActivityLogger.log_activity(
            action='offer_accepted',
            candidate_id=candidate_id
        )
