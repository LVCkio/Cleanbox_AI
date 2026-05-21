"""
CleanInbox AI — Ethical UX Router
Xử lý Snooze và Unsubscribe. Tuân thủ Nghị định 13/2023/NĐ-CP.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Literal
from backend.auth.jwt_handler import get_current_org, TokenData

router = APIRouter(prefix="/api/v1/ethical-ux", tags=["💚 Quản Lý Trải Nghiệm Văn Minh"])


# ─── Schemas ────────────────────────────────────────
class SnoozeRequest(BaseModel):
    contact_id: str
    snooze_days: Literal[30, 60, 90]

class UnsubscribeRequest(BaseModel):
    contact_id: str
    reason: str = "user_requested"   # user_requested | spam | irrelevant

class EthicalUxResponse(BaseModel):
    contact_id: str
    action: str
    message: str
    snooze_until: str | None = None


# ─── Endpoints ──────────────────────────────────────

@router.post("/snooze", response_model=EthicalUxResponse)
async def snooze_contact(
    payload: SnoozeRequest,
    current_org: TokenData = Depends(get_current_org),
):
    """
    Tạm dừng gửi email cho contact trong 30/60/90 ngày.
    Thay thế Unsubscribe — giảm tỷ lệ mất liên hệ vĩnh viễn.

    Tác động:
    - Cập nhật contacts.consent_status = 'snoozed'
    - Cập nhật contacts.snooze_until = NOW() + snooze_days
    - Cập nhật contacts.ethical_ux_flag = FALSE
    """
    snooze_until = datetime.utcnow() + timedelta(days=payload.snooze_days)

    # TODO: await db.execute(UPDATE contacts SET ... WHERE id = payload.contact_id AND org_id = current_org.org_id)

    return EthicalUxResponse(
        contact_id=payload.contact_id,
        action="snoozed",
        message=f"Đã tạm dừng {payload.snooze_days} ngày. Hệ thống sẽ tự động kích hoạt lại sau ngày {snooze_until.strftime('%d/%m/%Y')}.",
        snooze_until=snooze_until.isoformat(),
    )


@router.post("/unsubscribe", response_model=EthicalUxResponse)
async def unsubscribe_contact(
    payload: UnsubscribeRequest,
    current_org: TokenData = Depends(get_current_org),
):
    """
    Hủy đăng ký hoàn toàn.
    Theo Điều 17 NĐ13/2023: phải xử lý yêu cầu trong 72 giờ.

    Tác động:
    - contacts.consent_status = 'unsubscribed'
    - Xóa contact khỏi danh sách gửi trong provider (Mailchimp/HubSpot/SendGrid)
    - Ghi log audit trail bắt buộc
    """
    # TODO: await db.execute(UPDATE contacts SET consent_status = 'unsubscribed' ...)
    # TODO: await provider_service.unsubscribe(contact.provider_ref_id)
    # TODO: await audit_log.record(org_id, contact_id, action="unsubscribe", reason=payload.reason)

    return EthicalUxResponse(
        contact_id=payload.contact_id,
        action="unsubscribed",
        message="Đã hủy đăng ký thành công. Dữ liệu của bạn được xử lý theo Nghị định 13/2023/NĐ-CP.",
        snooze_until=None,
    )


@router.get("/status/{contact_id}")
async def get_ethical_ux_status(
    contact_id: str,
    current_org: TokenData = Depends(get_current_org),
):
    """Kiểm tra trạng thái Ethical UX của một contact."""
    # TODO: Query DB
    return {
        "contact_id": contact_id,
        "consent_status": "active",
        "ethical_ux_flag": False,
        "snooze_until": None,
        "last_bfs_score": None,
    }
