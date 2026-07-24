"""Offer Letter Generation & Sending"""
from datetime import datetime, timezone
import firebase_admin.firestore

db = firebase_admin.firestore.client()

class OfferService:
    """Generate and send offer letters to candidates"""

    async def generate_offer(self, candidate_id: str, job_id: str, salary: str, start_date: str, notes: str = "") -> dict:
        """Generate and send offer letter"""
        try:
            cand_doc = db.collection('candidates').document(candidate_id).get()
            if not cand_doc.exists:
                return {'error': 'Candidate not found'}

            job_doc = db.collection('jobs').document(job_id).get()
            if not job_doc.exists:
                return {'error': 'Job not found'}

            candidate_data = cand_doc.to_dict()
            job_data = job_doc.to_dict()

            # Create offer letter
            offer_data = {
                'candidate_id': candidate_id,
                'job_id': job_id,
                'candidate_name': candidate_data.get('name'),
                'candidate_email': candidate_data.get('email'),
                'job_title': job_data.get('title'),
                'salary': salary,
                'start_date': start_date,
                'notes': notes,
                'status': 'pending',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'expires_at': datetime.now(timezone.utc).isoformat()  # 30 days from now
            }

            # Save to Firestore
            db.collection('offers').document(candidate_id).set(offer_data)

            # Update candidate stage
            db.collection('candidates').document(candidate_id).update({
                'pipeline_stage': 'offer',
                'stage': 'offer'
            })

            return {
                'status': 'success',
                'message': f'Offer sent to {candidate_data.get("name")}',
                'offer_data': offer_data
            }
        except Exception as e:
            return {'error': str(e)}

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
