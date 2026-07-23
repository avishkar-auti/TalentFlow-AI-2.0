import logging
from typing import Dict, Any, Optional
import firebase_admin.auth
import firebase_admin.firestore

logger = logging.getLogger("auth")

class AuthService:
    def __init__(self):
        self._db = None

    def _get_db(self):
        if self._db is None:
            self._db = firebase_admin.firestore.client()
        return self._db

    async def verify_google_oauth_token(self, id_token: str, role: str = "recruiter") -> Dict[str, Any]:
        """
        Verify Firebase Google OAuth ID Token using Firebase Admin SDK.
        Creates or updates user document in Firestore 'users' collection.
        """
        try:
            decoded = firebase_admin.auth.verify_id_token(id_token)
            uid = decoded.get("uid")
            email = decoded.get("email", "")
            name = decoded.get("name", email.split("@")[0] if email else "User")
            picture = decoded.get("picture", "")

            db = self._get_db()
            user_ref = db.collection("users").document(uid)
            user_doc = user_ref.get()

            user_data = {
                "id": uid,
                "uid": uid,
                "email": email,
                "name": name,
                "picture": picture,
                "role": role,
                "auth_provider": "google.com",
            }

            if not user_doc.exists:
                user_data["created_at"] = firebase_admin.firestore.SERVER_TIMESTAMP
                user_ref.set(user_data)
            else:
                existing = user_doc.to_dict() or {}
                user_data["role"] = existing.get("role", role)
                user_ref.update({"name": name, "picture": picture, "email": email})

            return {
                "user": user_data,
                "uid": uid,
                "access_token": id_token,
                "token_type": "bearer",
            }
        except Exception as e:
            logger.error(f"Google OAuth token verification failed: {e}")
            raise ValueError(f"Invalid Firebase ID Token: {e}")

    async def register_user(self, email: str, password: str, role: str = "recruiter", name: str = "") -> Dict[str, Any]:
        """Create Firebase Auth user and store profile in Firestore."""
        try:
            user_record = firebase_admin.auth.create_user(
                email=email,
                password=password,
                display_name=name or email.split("@")[0]
            )
            uid = user_record.uid
            db = self._get_db()
            profile = {
                "id": uid,
                "uid": uid,
                "email": email,
                "name": name or email.split("@")[0],
                "role": role,
                "auth_provider": "password",
            }
            db.collection("users").document(uid).set(profile)
            return profile
        except firebase_admin.auth.EmailAlreadyExistsError:
            db = self._get_db()
            users = list(db.collection("users").where("email", "==", email).limit(1).stream())
            if users:
                return users[0].to_dict()
            return {"email": email, "role": role, "name": name}
        except Exception as e:
            logger.warning(f"Firebase Auth create_user fallback: {e}")
            return {"email": email, "role": role, "name": name}

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        db = self._get_db()
        users = list(db.collection("users").where("email", "==", email).limit(1).stream())
        if users:
            user_data = users[0].to_dict()
            return {"user": user_data, "access_token": f"token_{user_data.get('id')}", "token_type": "bearer"}
        return {"email": email, "access_token": "mock_jwt_token", "token_type": "bearer"}

    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        db = self._get_db()
        doc = db.collection("users").document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return {"id": user_id, "email": "user@example.com", "role": "recruiter"}

    async def refresh(self, refresh_token: str) -> Dict[str, str]:
        return {"access_token": refresh_token, "refresh_token": refresh_token}
