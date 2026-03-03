"""
Cost Intelligence Routes — /api/v1/costs/*

Pillar 2: API Cost Intelligence.
Exposes endpoints for cost tracking, breakdown, forecasting,
anomaly detection, optimization tips, ROI calculation, and model pricing.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from routes.auth import require_auth
from services.cost_intelligence import (
    calculate_cost,
    get_supported_models,
    compute_cost_breakdown,
    forecast_costs,
    detect_cost_anomalies,
    get_optimization_tips,
    calculate_roi,
    get_demo_cost_data,
)
from services.cache import cache_get, cache_set

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/costs", tags=["Cost Intelligence"])


# ── Request models ──────────────────────────────────────────────────────────

class LogCallRequest(BaseModel):
    provider: str = Field(..., max_length=100)
    model: str = Field(..., max_length=100)
    tokens_input: int = Field(0, ge=0)
    tokens_output: int = Field(0, ge=0)
    endpoint: str = Field("", max_length=500)
    latency_ms: float = Field(0, ge=0)
    status_code: int = Field(200)


class ROIRequest(BaseModel):
    monthly_api_spend: float = Field(..., ge=0, description="Current monthly API spend in USD")
    plan_cost: float = Field(29.0, ge=0)
    estimated_savings_pct: float = Field(30.0, ge=0, le=100)
    hours_saved_per_month: float = Field(10.0, ge=0)
    engineer_hourly_rate: float = Field(75.0, ge=0)


class BudgetRequest(BaseModel):
    name: str = Field(..., max_length=255)
    provider: str = Field("", max_length=100)
    monthly_limit_usd: float = Field(..., gt=0)
    alert_threshold_pct: float = Field(80, ge=0, le=100)
    auto_kill: bool = False


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/models")
async def list_models_endpoint(user=Depends(require_auth)):
    """List all supported AI models with pricing."""
    try:
        models = get_supported_models()
        return {"status": "ok", "models": models, "total": len(models)}
    except Exception as e:
        logger.error(f"List models failed: {e}")
        raise HTTPException(500, "Failed to list models")


@router.post("/calculate")
async def calculate_cost_endpoint(req: LogCallRequest, user=Depends(require_auth)):
    """Calculate cost for a single API call."""
    try:
        cost = calculate_cost(req.model, req.tokens_input, req.tokens_output)
        return {
            "status": "ok",
            "model": req.model,
            "tokens_input": req.tokens_input,
            "tokens_output": req.tokens_output,
            "cost_usd": cost,
        }
    except Exception as e:
        logger.error(f"Cost calculation failed: {e}")
        raise HTTPException(500, "Cost calculation failed")


@router.get("/breakdown")
async def cost_breakdown_endpoint(
    user=Depends(require_auth),
    days: int = Query(30, ge=1, le=365),
):
    """Get cost breakdown by provider, model, and day."""
    try:
        cache_key = f"cost_breakdown:{user.get('user_id', 0)}:{days}"
        cached = await cache_get(cache_key)
        if cached:
            return {"status": "ok", **cached, "cached": True}

        # Use demo data for now (real implementation queries api_call_logs table)
        demo = get_demo_cost_data()
        result = demo["breakdown"]
        await cache_set(cache_key, result, ttl=120)
        return {"status": "ok", **result, "cached": False}
    except Exception as e:
        logger.error(f"Cost breakdown failed: {e}")
        raise HTTPException(500, "Cost breakdown failed")


@router.get("/forecast")
async def cost_forecast_endpoint(
    user=Depends(require_auth),
    days_ahead: int = Query(30, ge=1, le=90),
):
    """Forecast future API costs based on historical usage."""
    try:
        cache_key = f"cost_forecast:{user.get('user_id', 0)}:{days_ahead}"
        cached = await cache_get(cache_key)
        if cached:
            return {"status": "ok", **cached, "cached": True}

        demo = get_demo_cost_data()
        result = demo["forecast"]
        await cache_set(cache_key, result, ttl=300)
        return {"status": "ok", **result, "cached": False}
    except Exception as e:
        logger.error(f"Cost forecast failed: {e}")
        raise HTTPException(500, "Cost forecast failed")


@router.get("/anomalies")
async def cost_anomalies_endpoint(user=Depends(require_auth)):
    """Detect cost anomalies and spending spikes."""
    try:
        demo = get_demo_cost_data()
        anomalies = demo["anomalies"]
        return {"status": "ok", "anomalies": anomalies, "total": len(anomalies)}
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        raise HTTPException(500, "Anomaly detection failed")


@router.get("/optimization")
async def optimization_tips_endpoint(user=Depends(require_auth)):
    """Get AI-powered cost optimization recommendations."""
    try:
        demo = get_demo_cost_data()
        tips = demo["optimization_tips"]
        total_potential_savings = sum(t.get("estimated_monthly_savings_usd", 0) for t in tips)
        return {
            "status": "ok",
            "tips": tips,
            "total": len(tips),
            "total_potential_monthly_savings_usd": round(total_potential_savings, 2),
        }
    except Exception as e:
        logger.error(f"Optimization tips failed: {e}")
        raise HTTPException(500, "Optimization tips failed")


@router.post("/roi")
async def roi_calculator_endpoint(req: ROIRequest, user=Depends(require_auth)):
    """Calculate ROI of using DevPulse."""
    try:
        result = calculate_roi(
            monthly_api_spend=req.monthly_api_spend,
            devpulse_plan_cost=req.plan_cost,
            estimated_savings_pct=req.estimated_savings_pct,
            hours_saved_per_month=req.hours_saved_per_month,
            engineer_hourly_rate=req.engineer_hourly_rate,
        )
        return {"status": "ok", **result}
    except Exception as e:
        logger.error(f"ROI calculation failed: {e}")
        raise HTTPException(500, "ROI calculation failed")


@router.get("/dashboard")
async def cost_dashboard_endpoint(user=Depends(require_auth)):
    """Get complete cost intelligence dashboard data."""
    try:
        cache_key = f"cost_dashboard:{user.get('user_id', 0)}"
        cached = await cache_get(cache_key)
        if cached:
            return {"status": "ok", **cached, "cached": True}

        demo = get_demo_cost_data()
        await cache_set(cache_key, demo, ttl=120)
        return {"status": "ok", **demo, "cached": False}
    except Exception as e:
        logger.error(f"Cost dashboard failed: {e}")
        raise HTTPException(500, "Cost dashboard failed")


@router.post("/budgets")
async def create_budget_endpoint(req: BudgetRequest, user=Depends(require_auth)):
    """Create a cost budget with alerts and optional auto-kill."""
    try:
        import uuid
        budget = {
            "id": str(uuid.uuid4())[:8],
            "user_id": user.get("user_id"),
            "name": req.name,
            "provider": req.provider,
            "monthly_limit_usd": req.monthly_limit_usd,
            "current_spend_usd": 0,
            "alert_threshold_pct": req.alert_threshold_pct,
            "auto_kill": req.auto_kill,
            "status": "active",
        }
        return {"status": "ok", "budget": budget}
    except Exception as e:
        logger.error(f"Create budget failed: {e}")
        raise HTTPException(500, "Budget creation failed")


@router.get("/budgets")
async def list_budgets_endpoint(user=Depends(require_auth)):
    """List all cost budgets for the user."""
    # Demo budgets
    budgets = [
        {
            "id": "bgt-001",
            "name": "OpenAI Monthly",
            "provider": "openai",
            "monthly_limit_usd": 500,
            "current_spend_usd": 342.50,
            "alert_threshold_pct": 80,
            "auto_kill": True,
            "usage_pct": 68.5,
            "status": "active",
        },
        {
            "id": "bgt-002",
            "name": "Anthropic Monthly",
            "provider": "anthropic",
            "monthly_limit_usd": 200,
            "current_spend_usd": 178.20,
            "alert_threshold_pct": 80,
            "auto_kill": False,
            "usage_pct": 89.1,
            "status": "warning",
        },
    ]
    return {"status": "ok", "budgets": budgets, "total": len(budgets)}
