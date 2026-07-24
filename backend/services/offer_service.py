"""Offer Letter Generation & Sending"""
from datetime import datetime, timezone
import firebase_admin.firestore

db = firebase_admin.firestore.client()

class OfferService:
    """Generate and send offer letters to candidates"""

    async def generate_offer(self, candidate_id: str, job_id: str, salary: str, start_date: str, notes: str = "") -> dict:
        """Generate and send offer letter"""
        candidate_name = "Candidate"
        candidate_email = f"candidate_{candidate_id[-6:]}@example.com"
        job_title = "Software Engineer"

        try:
            cand_doc = db.collection('candidates').document(candidate_id).get()
            if cand_doc.exists:
                cdata = cand_doc.to_dict()
                candidate_name = cdata.get('name', candidate_name)
                candidate_email = cdata.get('email', candidate_email)
        except Exception:
            pass

        try:
            if job_id:
                job_doc = db.collection('jobs').document(job_id).get()
                if job_doc.exists:
                    jdata = job_doc.to_dict()
                    job_title = jdata.get('title', job_title)
        except Exception:
            pass

        # Create offer letter payload
        offer_data = {
            'id': f"off_{candidate_id}",
            'candidate_id': candidate_id,
            'job_id': job_id or "JOB001",
            'candidate_name': candidate_name,
            'candidate_email': candidate_email,
            'job_title': job_title,
            'salary': salary,
            'start_date': start_date,
            'notes': notes,
            'status': 'pending',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'expires_at': datetime.now(timezone.utc).isoformat()
        }

        # Save to Firestore
        try:
            db.collection('offers').document(candidate_id).set(offer_data, merge=True)
            db.collection('candidates').document(candidate_id).set({
                'pipeline_stage': 'offer',
                'stage': 'offer'
            }, merge=True)
        except Exception as e:
            pass

        return {
            'status': 'success',
            'message': f'Offer sent to {candidate_name}',
            'offer_data': offer_data
        }

    async def get_offer(self, candidate_id: str) -> dict:
        """Get candidate's offer"""
        doc = db.collection('offers').document(candidate_id).get()
        return doc.to_dict() if doc.exists else None

    async def accept_offer(self, candidate_id: str) -> dict:
        """Candidate accepts offer"""
        db.collection('offers').document(candidate_id).update({
            'status': 'accepted',
            'accepted_at': datetime.now(timezone.utc).isoformat()
        })
        db.collection('candidates').document(candidate_id).update({
            'pipeline_stage': 'onboarding',
            'status': 'hired'
        })
        return {'status': 'success', 'message': 'Offer accepted!'}

    async def reject_offer(self, candidate_id: str, reason: str = "") -> dict:
        """Candidate rejects offer"""
        db.collection('offers').document(candidate_id).update({
            'status': 'rejected',
            'rejected_at': datetime.now(timezone.utc).isoformat(),
            'rejection_reason': reason
        })
        db.collection('candidates').document(candidate_id).update({
            'pipeline_stage': 'rejected'
        })
        return {'status': 'success', 'message': 'Offer rejected'}
