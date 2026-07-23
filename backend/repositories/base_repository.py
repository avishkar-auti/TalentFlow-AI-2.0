from typing import TypeVar, Generic, Type, Optional, Any, Dict, List, Tuple
from pydantic import BaseModel
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import logging
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1 import Query

from backend.firebase.firestore import db

logger = logging.getLogger('firebase')

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    """Generic repository for Firestore CRUD operations.
    Isolates all Firestore access behind a clean interface."""
    
    def __init__(self, collection_name: str, model_class: Type[T]):
        self.collection_name = collection_name
        self.model_class = model_class
        self._executor = ThreadPoolExecutor(max_workers=4)
        self.collection = db.collection(self.collection_name)
    
    def _run_sync(self, func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self._executor, lambda: func(*args, **kwargs))

    async def get(self, doc_id: str) -> Optional[T]:
        """Get document by ID, return as typed model."""
        try:
            doc_ref = self.collection.document(doc_id)
            doc = await self._run_sync(doc_ref.get)
            if doc.exists:
                return self.model_class(**doc.to_dict())
            return None
        except Exception as e:
            logger.error(f"Error getting document {doc_id} from {self.collection_name}: {e}")
            raise

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Get all documents with pagination."""
        try:
            query = self.collection.limit(limit).offset(offset)
            docs = await self._run_sync(query.stream)
            return [self.model_class(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting all documents from {self.collection_name}: {e}")
            raise
    
    async def create(self, doc_id: str, data: T) -> T:
        """Create a new document. Auto-adds createdAt, updatedAt."""
        try:
            doc_ref = self.collection.document(doc_id)
            data_dict = data.model_dump(exclude_unset=True)
            now = datetime.now(timezone.utc)
            if 'createdAt' not in data_dict:
                data_dict['createdAt'] = now
            data_dict['updatedAt'] = now
            await self._run_sync(doc_ref.set, data_dict)
            return self.model_class(**data_dict)
        except Exception as e:
            logger.error(f"Error creating document {doc_id} in {self.collection_name}: {e}")
            raise
    
    async def update(self, doc_id: str, data: dict) -> T:
        """Partial update. Auto-updates updatedAt."""
        try:
            doc_ref = self.collection.document(doc_id)
            data['updatedAt'] = datetime.now(timezone.utc)
            await self._run_sync(doc_ref.update, data)
            updated_doc = await self._run_sync(doc_ref.get)
            return self.model_class(**updated_doc.to_dict())
        except Exception as e:
            logger.error(f"Error updating document {doc_id} in {self.collection_name}: {e}")
            raise
    
    async def delete(self, doc_id: str) -> bool:
        """Delete document."""
        try:
            doc_ref = self.collection.document(doc_id)
            await self._run_sync(doc_ref.delete)
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id} from {self.collection_name}: {e}")
            return False
    
    async def query(self, filters: List[Tuple[str, str, Any]], order_by: Optional[str] = None, 
                    limit: int = 100, direction: str = 'DESCENDING') -> List[T]:
        """Query with filters. Each filter is (field, op, value)."""
        try:
            query_ref = self.collection
            for field, op, value in filters:
                query_ref = query_ref.where(filter=FieldFilter(field, op, value))
            
            if order_by:
                dir_enum = Query.DESCENDING if direction.upper() == 'DESCENDING' else Query.ASCENDING
                query_ref = query_ref.order_by(order_by, direction=dir_enum)
            
            query_ref = query_ref.limit(limit)
            docs = await self._run_sync(query_ref.stream)
            return [self.model_class(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Error querying {self.collection_name}: {e}")
            raise
    
    async def get_subcollection(self, doc_id: str, subcollection: str, 
                                 sub_doc_id: str = 'latest') -> Optional[Dict[str, Any]]:
        """Get a subcollection document (e.g., candidates/{id}/resume_analysis/latest)."""
        try:
            doc_ref = self.collection.document(doc_id).collection(subcollection).document(sub_doc_id)
            doc = await self._run_sync(doc_ref.get)
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting subcollection {subcollection}/{sub_doc_id} for {doc_id}: {e}")
            raise
    
    async def set_subcollection(self, doc_id: str, subcollection: str, 
                                 sub_doc_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Set a subcollection document."""
        try:
            doc_ref = self.collection.document(doc_id).collection(subcollection).document(sub_doc_id)
            data['updatedAt'] = datetime.now(timezone.utc)
            await self._run_sync(doc_ref.set, data)
            return data
        except Exception as e:
            logger.error(f"Error setting subcollection {subcollection}/{sub_doc_id} for {doc_id}: {e}")
            raise
    
    async def count(self, filters: Optional[List[Tuple[str, str, Any]]] = None) -> int:
        """Count documents matching filters."""
        try:
            query_ref = self.collection
            if filters:
                for field, op, value in filters:
                    query_ref = query_ref.where(filter=FieldFilter(field, op, value))
            count_query = query_ref.count()
            result = await self._run_sync(count_query.get)
            return result[0][0].value
        except Exception as e:
            logger.error(f"Error counting in {self.collection_name}: {e}")
            raise
    
    async def batch_create(self, items: Dict[str, T]) -> List[T]:
        """Batch create multiple documents."""
        try:
            batch = db.batch()
            now = datetime.now(timezone.utc)
            for doc_id, data in items.items():
                doc_ref = self.collection.document(doc_id)
                data_dict = data.model_dump(exclude_unset=True)
                if 'createdAt' not in data_dict:
                    data_dict['createdAt'] = now
                data_dict['updatedAt'] = now
                batch.set(doc_ref, data_dict)
            await self._run_sync(batch.commit)
            return list(items.values())
        except Exception as e:
            logger.error(f"Error in batch create for {self.collection_name}: {e}")
            raise
    
    async def exists(self, doc_id: str) -> bool:
        """Check if document exists."""
        try:
            doc_ref = self.collection.document(doc_id)
            doc = await self._run_sync(doc_ref.get)
            return doc.exists
        except Exception as e:
            logger.error(f"Error checking if {doc_id} exists in {self.collection_name}: {e}")
            raise
