"""
Firestore Index Generator & Management Tool for TalentFlow-AI.

Generates the `firestore.indexes.json` manifest file containing all composite index
definitions required for TalentFlow-AI Firestore queries. Provides instructions for
CLI deployment and direct links for manual creation.

Usage:
    python scripts/create_indexes.py [--output PATH]
"""

import sys
import os
import json
import argparse
import logging
from typing import List, Dict, Any

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("create_indexes")

# Project root resolution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_INDEXES_PATH = os.path.join(PROJECT_ROOT, "firestore.indexes.json")


def get_composite_indexes() -> Dict[str, Any]:
    """Define all composite indexes required by TalentFlow-AI queries."""
    return {
        "indexes": [
            {
                "collectionGroup": "candidates",
                "queryScope": "COLLECTION",
                "fields": [
                    { "fieldPath": "applied_job_id", "order": "ASCENDING" },
                    { "fieldPath": "pipeline_stage", "order": "ASCENDING" },
                    { "fieldPath": "created_at", "order": "DESCENDING" }
                ]
            },
            {
                "collectionGroup": "candidates",
                "queryScope": "COLLECTION",
                "fields": [
                    { "fieldPath": "applied_job_id", "order": "ASCENDING" },
                    { "fieldPath": "status", "order": "ASCENDING" },
                    { "fieldPath": "created_at", "order": "DESCENDING" }
                ]
            },
            {
                "collectionGroup": "jobs",
                "queryScope": "COLLECTION",
                "fields": [
                    { "fieldPath": "recruiter_id", "order": "ASCENDING" },
                    { "fieldPath": "status", "order": "ASCENDING" },
                    { "fieldPath": "created_at", "order": "DESCENDING" }
                ]
            },
            {
                "collectionGroup": "interviews",
                "queryScope": "COLLECTION",
                "fields": [
                    { "fieldPath": "candidate_id", "order": "ASCENDING" },
                    { "fieldPath": "scheduled_at", "order": "DESCENDING" }
                ]
            },
            {
                "collectionGroup": "interviews",
                "queryScope": "COLLECTION",
                "fields": [
                    { "fieldPath": "status", "order": "ASCENDING" },
                    { "fieldPath": "scheduled_at", "order": "ASCENDING" }
                ]
            },
            {
                "collectionGroup": "activity_logs",
                "queryScope": "COLLECTION",
                "fields": [
                    { "fieldPath": "entity_id", "order": "ASCENDING" },
                    { "fieldPath": "timestamp", "order": "DESCENDING" }
                ]
            }
        ],
        "fieldOverrides": []
    }


def create_indexes(output_path: str):
    """Generate firestore.indexes.json and display deployment instructions."""
    logger.info("Generating Cloud Firestore composite index definitions...")
    
    index_data = get_composite_indexes()
    
    # Save to JSON file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2)
        
    logger.info(f"Successfully created index definition file at: {output_path}")
    
    print("\n" + "=" * 75)
    print("           TALENTFLOW-AI FIRESTORE COMPOSITE INDEXES SUMMARY")
    print("=" * 75)
    
    for i, idx in enumerate(index_data["indexes"], start=1):
        fields_str = ", ".join([f"{field['fieldPath']} ({field['order']})" for field in idx['fields']])
        print(f"{i}. Collection: {idx['collectionGroup']}")
        print(f"   Fields:     {fields_str}")
        print(f"   Scope:      {idx['queryScope']}\n")
        
    print("=" * 75)
    print("                  MANUAL & CLI DEPLOYMENT INSTRUCTIONS")
    print("=" * 75)
    print("Option 1: Deploy using Firebase CLI (Recommended)")
    print("   1. Install Firebase CLI: npm install -g firebase-tools")
    print("   2. Login to Firebase:   firebase login")
    print("   3. Deploy indexes:      firebase deploy --only firestore:indexes")
    print("\nOption 2: Direct GCP / Firebase Console URL")
    print("   https://console.firebase.google.com/project/_/firestore/indexes")
    print("=" * 75 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Create firestore.indexes.json for TalentFlow-AI.")
    parser.add_argument("--output", type=str, default=DEFAULT_INDEXES_PATH, help="Target JSON output path")
    args = parser.parse_args()
    
    create_indexes(args.output)


if __name__ == "__main__":
    main()
