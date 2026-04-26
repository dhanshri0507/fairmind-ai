"""
Supabase (Firestore-like) service for storing and retrieving audit results.
"""

import os
import json
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

load_dotenv()
logger = logging.getLogger("fairmind.storage")

_client: Optional[Client] = None


def get_client() -> Client:
    """Lazily create the Supabase client, reading env vars at first call."""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL", "").strip()
        key = os.getenv("SUPABASE_KEY", "").strip()

        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables. "
                f"Got URL={url!r}, KEY={'<set>' if key else '<empty>'}"
            )

        logger.info("Connecting to Supabase at %s", url)
        _client = create_client(url, key)
        logger.info("Supabase client initialised successfully.")
    return _client


async def save_audit(audit_id: str, results: Dict[str, Any]) -> None:
    """Persist audit results to Supabase audits table."""
    try:
        client = get_client()
        client.table("audits").upsert(
            {
                "id": audit_id,
                "results": results,
                "filename": results.get("filename", ""),
                "overall_bias_detected": results.get("overall_bias_detected", False),
                "fairness_score": results.get("fairness_score", 0),
                "dataset_size": results.get("dataset_size", 0),
            }
        ).execute()
    except Exception as e:
        # Non-fatal: log and continue
        logger.exception("save_audit failed (audit_id=%s)", audit_id)


async def get_audit(audit_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve audit results from Supabase by audit_id."""
    try:
        client = get_client()
        resp = client.table("audits").select("*").eq("id", audit_id).single().execute()
        if resp.data:
            return resp.data.get("results")
        return None
    except Exception as e:
        logger.exception("get_audit failed (audit_id=%s)", audit_id)
        return None


async def list_audits(limit: int = 20) -> list:
    """List recent audits."""
    try:
        client = get_client()
        resp = (
            client.table("audits")
            .select("id, filename, fairness_score, overall_bias_detected, dataset_size")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data or []
    except Exception as e:
        logger.exception("list_audits failed (limit=%s)", limit)
        return []
