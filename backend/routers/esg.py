"""
CleanInbox AI — ESG Reporter Router
API cấp dữ liệu cho ESG Dashboard.
"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from backend.auth.jwt_handler import get_current_org, TokenData
from backend.config import settings

router = APIRouter(prefix="/api/v1/esg", tags=["🌱 Báo Cáo Phát Triển Bền Vững"])


# ─── Schemas ────────────────────────────────────────
class CO2Stats(BaseModel):
    emails_filtered: int
    co2_saved_grams: float
    co2_saved_kg: float
    co2_saved_ton: float
    co2_unit: str           # "g" | "kg" | "tấn"
    cost_saved_usd: float
    progress_pct: float     # % tiến độ mục tiêu 1.5 tấn
    target_kg: float

class MonthlyStat(BaseModel):
    month: str
    emails_filtered: int
    co2_kg: float
    cost_usd: float

class ESGSummary(BaseModel):
    overall: CO2Stats
    monthly: List[MonthlyStat]
    campaign_count: int
    org_id: str


# ─── Helper: Chuyển đổi đơn vị CO2 ────────────────
def format_co2(grams: float) -> tuple[float, str]:
    """Chuyển đổi linh hoạt: g → kg → tấn."""
    kg  = grams / 1000
    ton = kg / 1000
    if ton >= 1:   return round(ton, 3), "tấn"
    if kg  >= 1:   return round(kg, 2),  "kg"
    return round(grams, 1), "g"


# ─── Endpoints ──────────────────────────────────────

@router.get("/summary", response_model=ESGSummary)
async def get_esg_summary(
    current_org: TokenData = Depends(get_current_org),
):
    """
    Tổng hợp toàn bộ số liệu ESG của tổ chức.
    Đây là API chính cấp dữ liệu cho ESG Dashboard.
    """
    # ── Mock data (TODO: thay bằng DB query) ──
    total_filtered = 2_480_000
    co2_grams = total_filtered * settings.CO2_PER_EMAIL_GRAMS
    co2_kg    = co2_grams / 1000
    co2_ton   = co2_kg / 1000
    cost_usd  = total_filtered * settings.COST_PER_EMAIL_USD
    progress  = min((co2_kg / settings.CO2_TARGET_KG) * 100, 100)
    val, unit = format_co2(co2_grams)

    overall = CO2Stats(
        emails_filtered=total_filtered,
        co2_saved_grams=round(co2_grams, 1),
        co2_saved_kg=round(co2_kg, 2),
        co2_saved_ton=round(co2_ton, 4),
        co2_unit=unit,
        cost_saved_usd=round(cost_usd, 2),
        progress_pct=round(progress, 1),
        target_kg=settings.CO2_TARGET_KG,
    )

    monthly = [
        MonthlyStat(month="T12", emails_filtered=227_000, co2_kg=68.1,  cost_usd=4_540),
        MonthlyStat(month="T1",  emails_filtered=317_000, co2_kg=95.1,  cost_usd=6_340),
        MonthlyStat(month="T2",  emails_filtered=373_000, co2_kg=111.9, cost_usd=7_460),
        MonthlyStat(month="T3",  emails_filtered=447_000, co2_kg=134.1, cost_usd=8_940),
        MonthlyStat(month="T4",  emails_filtered=593_000, co2_kg=177.9, cost_usd=11_860),
        MonthlyStat(month="T5",  emails_filtered=523_000, co2_kg=213.0, cost_usd=14_660),
    ]

    return ESGSummary(
        overall=overall,
        monthly=monthly,
        campaign_count=24,
        org_id=current_org.org_id,
    )


@router.get("/export")
async def export_esg_report(
    format: str = Query(default="json", enum=["json", "csv"]),
    current_org: TokenData = Depends(get_current_org),
):
    """
    Xuất báo cáo ESG theo chuẩn GHG Protocol Scope 3 — Category 11.
    Phục vụ báo cáo phát triển bền vững hướng tới Net Zero 2050.
    """
    report = {
        "report_name": "CleanInbox AI — ESG Impact Report",
        "standard": "GHG Protocol Scope 3, Category 11 (Use of Sold Products)",
        "compliance": "Nghị định 13/2023/NĐ-CP",
        "generated_at": "2025-05-19T16:00:00Z",
        "organization_id": current_org.org_id,
        "reporting_period": "2024-12 to 2025-05",
        "metrics": {
            "total_emails_filtered": 2_480_000,
            "co2_saved_kg": 744.0,
            "co2_saved_ton": 0.744,
            "cost_saved_usd": 49_600,
            "progress_to_annual_target_pct": 49.6,
            "annual_target_ton": 1.5,
        },
        "methodology": "CO2 = emails_filtered × 0.3g (nguồn: OurWorldInData Digital Carbon Footprint)",
        "net_zero_pathway": "Dự kiến đạt 1.5 tấn CO2 cắt giảm vào tháng 11/2025",
    }
    return report
