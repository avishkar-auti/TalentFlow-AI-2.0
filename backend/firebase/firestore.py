"""
Firestore client wrapper.
"""
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timezone

from firebase_admin import firestore
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.base_query import FieldFilter, BaseQuery

from .firebase import get_firebase_app

logger = logging.getLogger("firebase")

_firestore_client: Optional[Client] = None
_executor = ThreadPoolExecutor(max_workers=10)

def get_firestore_client() -> Client:
    """
    Get the Firestore client singleton.
    """
    global _firestore_client
    if _firestore_client is None:
        app = get_firebase_app()
        if app is None:
            # Fallback for dev mode
            logger.warning("Firebase app not initialized. Operating in lazy mock/dev mode.")
            try:
                _firestore_client = firestore.client()
            except Exception:
                pass
        else:
            try:
                _firestore_client = firestore.client(app=app)
                logger.info("Firestore client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Firestore client: {e}")
                raise
    return _firestore_client

class FirestoreProxy:
    """Dynamic proxy delegating to get_firestore_client()."""
    def __getattr__(self, name):
        client = get_firestore_client()
        if client is None:
            raise RuntimeError("Firestore client is unavailable.")
        return getattr(client, name)

db = FirestoreProxy()

async def _run_async(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_executor, lambda: func(*args, **kwargs))


async def get_document(collection: str, document_id: str) -> Optional[Dict[str, Any]]:
    """Get a document asynchronously."""
    try:
        client = get_firestore_client()
        if not client:
            return None
        doc_ref = client.collection(collection).document(document_id)
        
        def _get():
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
            
        return await _run_async(_get)
    except Exception as e:
        logger.warning(f"Error getting document {collection}/{document_id}: {e}")
        return None


async def set_document(collection: str, document_id: str, data: Dict[str, Any], merge: bool = True) -> None:
    """Set or create a document."""
    try:
        client = get_firestore_client()
        if not client:
            return
        doc_ref = client.collection(collection).document(document_id)
        
        now = datetime.now(timezone.utc)
        if "createdAt" not in data and not merge:
            data["createdAt"] = now
        data["updatedAt"] = now

        def _set():
            doc_ref.set(data, merge=merge)
            
        await _run_async(_set)
        logger.debug(f"Document {collection}/{document_id} set successfully.")
    except Exception as e:
        logger.warning(f"Error setting document {collection}/{document_id}: {e}")


async def update_document(collection: str, document_id: str, data: Dict[str, Any]) -> None:
    """Update an existing document."""
    try:
        client = get_firestore_client()
        if not client:
            return
        doc_ref = client.collection(collection).document(document_id)
        data["updatedAt"] = datetime.now(timezone.utc)

        def _update():
            doc_ref.update(data)
            
        await _run_async(_update)
        logger.debug(f"Document {collection}/{document_id} updated successfully.")
    except Exception as e:
        logger.warning(f"Error updating document {collection}/{document_id}: {e}")


async def delete_document(collection: str, document_id: str) -> None:
    """Delete a document."""
    try:
        client = get_firestore_client()
        if not client:
            return
        doc_ref = client.collection(collection).document(document_id)

        def _delete():
            doc_ref.delete()
            
        await _run_async(_delete)
        logger.debug(f"Document {collection}/{document_id} deleted successfully.")
    except Exception as e:
        logger.warning(f"Error deleting document {collection}/{document_id}: {e}")


async def query_collection(
    collection: str, 
    filters: Optional[List[Tuple[str, str, Any]]] = None,
    order_by: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Query a collection with filters, ordering and limit."""
    try:
        client = get_firestore_client()
        if not client:
            return []
        query_ref: Union[Client, BaseQuery] = client.collection(collection)
        
        if filters:
            for field, op, value in filters:
                query_ref = query_ref.where(filter=FieldFilter(field, op, value))
                
        if order_by:
            direction = firestore.Query.DESCENDING if order_by.startswith("-") else firestore.Query.ASCENDING
            field = order_by.lstrip("-")
            query_ref = query_ref.order_by(field, direction=direction)
            
        if limit:
            query_ref = query_ref.limit(limit)

        def _query():
            docs = query_ref.stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
            
        return await _run_async(_query)
    except Exception as e:
        logger.warning(f"Error querying collection {collection}: {e}")
        return []


async def batch_write(writes: List[Tuple[str, str, str, Dict[str, Any]]]) -> None:
    """
    Perform a batch write.
    writes: list of tuples (operation, collection, document_id, data)
    """
    try:
        client = get_firestore_client()
        if not client:
            return
        
        def _batch():
            batch = client.batch()
            now = datetime.now(timezone.utc)
            
            for op, coll, doc_id, data in writes:
                doc_ref = client.collection(coll).document(doc_id)
                if op == 'set':
                    if "createdAt" not in data:
                        data["createdAt"] = now
                    data["updatedAt"] = now
                    batch.set(doc_ref, data, merge=True)
                elif op == 'update':
                    data["updatedAt"] = now
                    batch.update(doc_ref, data)
                elif op == 'delete':
                    batch.delete(doc_ref)
                    
            batch.commit()
            
        await _run_async(_batch)
        logger.debug(f"Batch write with {len(writes)} operations completed.")
    except Exception as e:
        logger.warning(f"Error executing batch write: {e}")
