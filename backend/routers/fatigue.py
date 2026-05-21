"""
CleanInbox AI — Fatigue Intelligence Router
Expose BFS calculator dưới dạng REST API endpoint.
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from fatigue_intelligence.bfs_calculator import MicroBehaviorInput, calculate_bfs, RiskLevel
from backend.auth.jwt_handler import get_current_org, TokenData

router = APIRouter(prefix="/api/v1/fatigue", tags=["🧠 Trí Tuệ Mệt Mỏi Thương Hiệu"])


# ─── Schemas ────────────────────────────────────────
class BFSRequest(BaseModel):
    contact_id: str
    time_spent_seconds: float
    consecutive_unread_deletes: int
    received_frequency_per_week: float
    last_open_days_ago: int = 0
    total_emails_received: int = 0

class BFSResponse(BaseModel):
    contact_id: str
    bfs_score: float
    risk_level: str
    ethical_ux_flag: bool
    recommended_action: str
    sub_scores: dict
    explanation: str


# ─── Endpoints ──────────────────────────────────────

@router.post("/calculate", response_model=BFSResponse)
async def calculate_brand_fatigue(
    payload: BFSRequest,
    background_tasks: BackgroundTasks,
    current_org: TokenData = Depends(get_current_org),
):
    """
    Tính Brand Fatigue Score cho một contact.
    Nếu BFS > 80: tự động kích hoạt cờ Ethical UX.
    Kết quả được lưu vào bảng brand_fatigue_scores.
    """
    data = MicroBehaviorInput(
        contact_id=payload.contact_id,
        time_spent_seconds=payload.time_spent_seconds,
        consecutive_unread_deletes=payload.consecutive_unread_deletes,
        received_frequency_per_week=payload.received_frequency_per_week,
        last_open_days_ago=payload.last_open_days_ago,
        total_emails_received=payload.total_emails_received,
    )
    result = calculate_bfs(data)

    # TODO: background_tasks.add_task(save_bfs_to_db, result, current_org.org_id)
    # TODO: if result.ethical_ux_flag → publish event to message queue

    return BFSResponse(
        contact_id=result.contact_id,
        bfs_score=result.bfs_score,
        risk_level=result.risk_level.value,
        ethical_ux_flag=result.ethical_ux_flag,
        recommended_action=result.recommended_action,
        sub_scores={
            "time_spent": result.sub_score_time_spent,
            "delete_unread": result.sub_score_delete_unread,
            "frequency": result.sub_score_frequency,
        },
        explanation=result.explanation,
    )


@router.post("/batch-calculate")
async def batch_calculate_bfs(
    payloads: list[BFSRequest],
    current_org: TokenData = Depends(get_current_org),
):
    """
    Tính BFS hàng loạt cho nhiều contacts cùng lúc.
    Dùng khi sync toàn bộ danh sách từ Mailchimp/HubSpot.
    """
    results = []
    critical_contacts = []

    for p in payloads:
        data = MicroBehaviorInput(
            contact_id=p.contact_id,
            time_spent_seconds=p.time_spent_seconds,
            consecutive_unread_deletes=p.consecutive_unread_deletes,
            received_frequency_per_week=p.received_frequency_per_week,
            last_open_days_ago=p.last_open_days_ago,
        )
        r = calculate_bfs(data)
        results.append({"contact_id": r.contact_id, "bfs_score": r.bfs_score, "risk": r.risk_level.value})
        if r.ethical_ux_flag:
            critical_contacts.append(r.contact_id)

    return {
        "total_processed": len(results),
        "critical_count": len(critical_contacts),
        "critical_contact_ids": critical_contacts,
        "results": results,
    }
