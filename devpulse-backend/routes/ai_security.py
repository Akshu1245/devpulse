"""
AI Security Scanner Routes — /api/v1/security/*

Pillar 1: The AI API Security Scanner.
Exposes endpoints for token leak detection, agent attack scanning,
OWASP API Top 10, full scans, fix suggestions, threat feed, and API inventory.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field

from routes.auth import require_auth
from services.ai_security_engine import (
    scan_token_leaks,
    scan_agent_attacks,
    scan_owasp_api,
    full_security_scan,
    generate_fix_suggestions,
    get_threat_feed,
    scan_api_inventory,
)
from services.cache import cache_get, cache_set, security_scan_key, make_code_hash

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/security", tags=["AI Security"])


# ── Request / Response models ───────────────────────────────────────────────

class ScanRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=500_000, description="Source code to scan")
    language: str = Field("python", max_length=30)


class FixRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=500_000)
    findings: list = Field(default_factory=list)


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/scan/tokens")
async def scan_tokens_endpoint(req: ScanRequest, user=Depends(require_auth)):
    """Scan code for leaked tokens, API keys, and secrets."""
    try:
        result = scan_token_leaks(req.code)
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"Token scan failed: {e}")
        raise HTTPException(500, "Token scan failed")


@router.post("/scan/agents")
async def scan_agents_endpoint(req: ScanRequest, user=Depends(require_auth)):
    """Scan code for AI agent attack vectors (prompt injection, SSRF, etc.)."""
    try:
        result = scan_agent_attacks(req.code)
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"Agent scan failed: {e}")
        raise HTTPException(500, "Agent attack scan failed")


@router.post("/scan/owasp")
async def scan_owasp_endpoint(req: ScanRequest, user=Depends(require_auth)):
    """Scan for OWASP API Security Top 10 (2023) issues."""
    try:
        result = scan_owasp_api(req.code)
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"OWASP scan failed: {e}")
        raise HTTPException(500, "OWASP scan failed")


@router.post("/scan/full")
async def full_scan_endpoint(req: ScanRequest, user=Depends(require_auth)):
    """Run complete security scan (tokens + agents + OWASP). Returns composite score. Cached 5 min."""
    try:
        code_hash = make_code_hash(req.code)
        key = security_scan_key(code_hash)
        cached = await cache_get(key)
        if cached:
            return {"status": "ok", **cached, "cached": True}

        result = full_security_scan(req.code, req.language)
        await cache_set(key, result, ttl=300)
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"Full scan failed: {e}")
        raise HTTPException(500, "Full security scan failed")


@router.post("/fix-suggestions")
async def fix_suggestions_endpoint(req: FixRequest, user=Depends(require_auth)):
    """Generate AI-powered fix suggestions for security findings."""
    try:
        suggestions = await generate_fix_suggestions(req.findings, req.code)
        return {
            "status": "ok",
            "suggestions": suggestions,
            "total": len(suggestions),
        }
    except Exception as e:
        logger.error(f"Fix suggestions failed: {e}")
        raise HTTPException(500, "Fix suggestion generation failed")


@router.get("/threat-feed")
async def threat_feed_endpoint(user=Depends(require_auth)):
    """Get real-time AI/API threat intelligence feed."""
    try:
        # Cache for 5 minutes
        cached = await cache_get("threat_feed")
        if cached:
            return {"status": "ok", "threats": cached, "cached": True}

        threats = get_threat_feed()
        await cache_set("threat_feed", threats, ttl=300)
        return {"status": "ok", "threats": threats, "cached": False}
    except Exception as e:
        logger.error(f"Threat feed failed: {e}")
        raise HTTPException(500, "Threat feed unavailable")


@router.post("/inventory")
async def api_inventory_endpoint(req: ScanRequest, user=Depends(require_auth)):
    """Discover AI/API providers used in code."""
    try:
        result = scan_api_inventory(req.code)
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"Inventory scan failed: {e}")
        raise HTTPException(500, "API inventory scan failed")


@router.get("/score-history")
async def score_history_endpoint(
    user=Depends(require_auth),
    limit: int = 20,
):
    """Get security scan score history for the current user (demo data)."""
    import random
    random.seed(user.get("user_id", 1))
    history = []
    for i in range(min(limit, 50)):
        score = max(0, min(100, random.gauss(75, 15)))
        history.append({
            "scan_id": i + 1,
            "score": round(score),
            "grade": (
                "A+" if score >= 97 else "A" if score >= 90 else
                "B" if score >= 75 else "C" if score >= 60 else
                "D" if score >= 40 else "F"
            ),
            "threats_found": max(0, int((100 - score) / 10)),
            "scan_type": random.choice(["full", "token_leak", "agent_attack"]),
            "scanned_at": f"2025-01-{max(1, 31 - i):02d}T12:00:00Z",
        })
    return {"status": "ok", "history": history}
