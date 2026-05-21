"""
CleanInbox AI — Fatigue Intelligence Module
============================================
Tính toán Brand Fatigue Score (BFS) từ 1–100 dựa trên hành vi vi mô.
BFS > 80 → kích hoạt cờ cảnh báo sang Ethical UX Manager.

Tác giả: CleanInbox AI Engineering
Phiên bản: 1.0.0-MVP
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import math


# ─────────────────────────────────────────────
# 1. ĐỊNH NGHĨA CÁC NGƯỠNG & TRỌNG SỐ
# ─────────────────────────────────────────────

class RiskLevel(Enum):
    LOW = "low"           # BFS 1–40
    MEDIUM = "medium"     # BFS 41–65
    HIGH = "high"         # BFS 66–80
    CRITICAL = "critical" # BFS 81–100 → kích hoạt Ethical UX

# Trọng số đóng góp vào BFS (tổng = 1.0)
WEIGHTS = {
    "time_spent":   0.30,   # Thời gian đọc email (30%)
    "delete_unread": 0.45,  # Xóa không đọc liên tiếp (45%) — tín hiệu mạnh nhất
    "frequency":    0.25,   # Tần suất nhận thư (25%)
}

# Ngưỡng chuẩn hóa các chỉ số đầu vào
THRESHOLDS = {
    "time_spent_max_sec": 120,       # Trên 120s = đọc kỹ (tốt)
    "time_spent_min_sec": 3,         # Dưới 3s = không đọc (xấu)
    "delete_unread_critical": 10,    # 10+ lần xóa liên tiếp = ngưỡng tối đa
    "freq_ideal_per_week": 1.5,      # 1.5 mail/tuần là lý tưởng
    "freq_max_per_week": 7,          # 7+ mail/tuần = spam territory
}


# ─────────────────────────────────────────────
# 2. DATA CLASSES
# ─────────────────────────────────────────────

@dataclass
class MicroBehaviorInput:
    """Dữ liệu đầu vào từ hành vi vi mô của một contact."""
    contact_id: str
    time_spent_seconds: float        # Tổng thời gian đọc email (giây)
    consecutive_unread_deletes: int  # Số email xóa liên tiếp không đọc
    received_frequency_per_week: float  # Trung bình số mail nhận / tuần
    # Metadata bổ sung (tùy chọn)
    total_emails_received: int = 0
    last_open_days_ago: int = 0      # Bao nhiêu ngày trước lần mở cuối


@dataclass
class BFSResult:
    """Kết quả tính toán Brand Fatigue Score."""
    contact_id: str
    bfs_score: float                 # Điểm tổng hợp 1–100
    risk_level: RiskLevel
    # Điểm thành phần (để audit/debug)
    sub_score_time_spent: float
    sub_score_delete_unread: float
    sub_score_frequency: float
    # Hành động khuyến nghị
    ethical_ux_flag: bool            # True nếu BFS > 80
    recommended_action: str
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    explanation: str = ""


# ─────────────────────────────────────────────
# 3. CÁC HÀM CHUẨN HÓA TỪNG THÀNH PHẦN
# ─────────────────────────────────────────────

def normalize_time_spent(seconds: float) -> float:
    """
    Chuẩn hóa thời gian đọc → điểm mệt mỏi (0.0 → 1.0).
    Logic: Đọc ít → mệt mỏi nhiều. Đọc nhiều → tốt, ít mệt.
    Dùng hàm sigmoid nghịch để có độ nhạy cao ở vùng ngưỡng thấp.
    """
    t_min = THRESHOLDS["time_spent_min_sec"]
    t_max = THRESHOLDS["time_spent_max_sec"]

    if seconds >= t_max:
        return 0.0   # Đọc kỹ → mệt mỏi = 0
    if seconds <= t_min:
        return 1.0   # Hầu như không mở → mệt mỏi = 100%

    # Chuẩn hóa tuyến tính trong khoảng [t_min, t_max]
    ratio = (seconds - t_min) / (t_max - t_min)
    return round(1.0 - ratio, 4)


def normalize_delete_unread(count: int) -> float:
    """
    Chuẩn hóa số lần xóa không đọc → điểm mệt mỏi (0.0 → 1.0).
    Dùng hàm logarithm để tăng độ nhạy ở giá trị thấp.
    """
    if count <= 0:
        return 0.0

    max_count = THRESHOLDS["delete_unread_critical"]
    # log(count+1) / log(max+1) — chuẩn hóa logarithmic
    score = math.log(count + 1) / math.log(max_count + 1)
    return round(min(score, 1.0), 4)


def normalize_frequency(mails_per_week: float) -> float:
    """
    Chuẩn hóa tần suất nhận thư → điểm mệt mỏi (0.0 → 1.0).
    Tần suất lý tưởng: 1–2 mail/tuần. Càng nhiều → càng mệt.
    """
    ideal = THRESHOLDS["freq_ideal_per_week"]
    max_freq = THRESHOLDS["freq_max_per_week"]

    if mails_per_week <= ideal:
        return 0.0   # Tần suất lý tưởng hoặc thấp → không gây mệt

    excess = mails_per_week - ideal
    max_excess = max_freq - ideal
    score = excess / max_excess
    return round(min(score, 1.0), 4)


# ─────────────────────────────────────────────
# 4. HÀM CHÍNH: TÍNH BFS
# ─────────────────────────────────────────────

def calculate_bfs(data: MicroBehaviorInput) -> BFSResult:
    """
    Tính Brand Fatigue Score (BFS) và xác định hành động cần thực hiện.

    Công thức tổng hợp:
        BFS_raw = w1*S_time + w2*S_delete + w3*S_freq  (trong khoảng 0–1)
        BFS     = BFS_raw * 100                         (quy về thang 1–100)

    Bonus penalty: Nếu contact không mở email > 30 ngày → cộng thêm 10 điểm.
    """

    # Tính điểm thành phần
    s_time   = normalize_time_spent(data.time_spent_seconds)
    s_delete = normalize_delete_unread(data.consecutive_unread_deletes)
    s_freq   = normalize_frequency(data.received_frequency_per_week)

    # Tổng hợp có trọng số
    bfs_raw = (
        WEIGHTS["time_spent"]    * s_time   +
        WEIGHTS["delete_unread"] * s_delete +
        WEIGHTS["frequency"]     * s_freq
    )

    # Penalty: contact "ma" — không mở email trên 30 ngày
    inactivity_penalty = 0.10 if data.last_open_days_ago > 30 else 0.0
    bfs_raw = min(bfs_raw + inactivity_penalty, 1.0)

    # Quy về thang điểm 1–100
    bfs_score = round(max(1.0, bfs_raw * 100), 2)

    # Xác định mức độ rủi ro
    if bfs_score <= 40:
        risk = RiskLevel.LOW
    elif bfs_score <= 65:
        risk = RiskLevel.MEDIUM
    elif bfs_score <= 80:
        risk = RiskLevel.HIGH
    else:
        risk = RiskLevel.CRITICAL

    # ── Kích hoạt cờ Ethical UX nếu BFS > 80 ──
    ethical_ux_flag = bfs_score > 80

    # Xác định hành động khuyến nghị
    if ethical_ux_flag:
        action = "TRIGGER_ETHICAL_UX_POPUP"   # Hiển thị popup chia tay văn minh
    elif risk == RiskLevel.HIGH:
        action = "SEND_RE_ENGAGEMENT_EMAIL"   # Gửi email giữ chân
    elif risk == RiskLevel.MEDIUM:
        action = "REDUCE_FREQUENCY"           # Giảm tần suất gửi
    else:
        action = "MAINTAIN_CURRENT_STRATEGY"  # Giữ nguyên chiến lược

    # Tạo giải thích tự động
    drivers = []
    if s_delete > 0.6:
        drivers.append(f"xóa không đọc liên tiếp ({data.consecutive_unread_deletes} lần)")
    if s_time > 0.6:
        drivers.append(f"thời gian đọc quá ngắn ({data.time_spent_seconds}s)")
    if s_freq > 0.5:
        drivers.append(f"tần suất gửi cao ({data.received_frequency_per_week:.1f} mail/tuần)")

    explanation = f"BFS={bfs_score} | Nguyên nhân chính: {', '.join(drivers) if drivers else 'tổng hợp nhiều yếu tố'}"

    return BFSResult(
        contact_id=data.contact_id,
        bfs_score=bfs_score,
        risk_level=risk,
        sub_score_time_spent=round(s_time * 100, 2),
        sub_score_delete_unread=round(s_delete * 100, 2),
        sub_score_frequency=round(s_freq * 100, 2),
        ethical_ux_flag=ethical_ux_flag,
        recommended_action=action,
        explanation=explanation,
    )


# ─────────────────────────────────────────────
# 5. MOCK EVENT HANDLER — Kích hoạt Ethical UX
# ─────────────────────────────────────────────

def handle_ethical_ux_trigger(result: BFSResult):
    """
    Mô phỏng việc gửi sự kiện sang Ethical UX Manager
    khi BFS vượt ngưỡng 80.
    """
    if not result.ethical_ux_flag:
        return

    payload = {
        "event": "ETHICAL_UX_TRIGGER",
        "contact_id": result.contact_id,
        "bfs_score": result.bfs_score,
        "risk_level": result.risk_level.value,
        "timestamp": result.calculated_at.isoformat(),
        "popup_config": {
            "show_snooze_options": [30, 60, 90],  # ngày
            "show_unsubscribe": True,
            "tone": "gentle",
        }
    }
    # Trong production: gọi Internal Message Queue (Kafka/RabbitMQ)
    print(f"\n🚨 [ETHICAL UX TRIGGER] Payload gửi đi: {payload}\n")
    return payload


# ─────────────────────────────────────────────
# 6. DEMO / SIMULATION
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  CleanInbox AI — Brand Fatigue Score Calculator v1.0")
    print("=" * 60)

    # Tập dữ liệu mô phỏng 4 loại contact điển hình
    test_cases = [
        MicroBehaviorInput(
            contact_id="contact_001",
            time_spent_seconds=85,
            consecutive_unread_deletes=1,
            received_frequency_per_week=1.0,
            last_open_days_ago=2,
        ),  # → Khách hàng tích cực

        MicroBehaviorInput(
            contact_id="contact_002",
            time_spent_seconds=15,
            consecutive_unread_deletes=5,
            received_frequency_per_week=4.0,
            last_open_days_ago=10,
        ),  # → Bắt đầu mệt mỏi

        MicroBehaviorInput(
            contact_id="contact_003",
            time_spent_seconds=5,
            consecutive_unread_deletes=8,
            received_frequency_per_week=6.0,
            last_open_days_ago=20,
        ),  # → Ngưỡng cao - cần can thiệp

        MicroBehaviorInput(
            contact_id="contact_004",
            time_spent_seconds=2,
            consecutive_unread_deletes=12,
            received_frequency_per_week=7.0,
            last_open_days_ago=45,
        ),  # → CRITICAL - kích hoạt Ethical UX
    ]

    for data in test_cases:
        result = calculate_bfs(data)
        print(f"\n📧 Contact: {result.contact_id}")
        print(f"   BFS Score  : {result.bfs_score}/100")
        print(f"   Risk Level : {result.risk_level.value.upper()}")
        print(f"   Sub-scores : time={result.sub_score_time_spent} | "
              f"delete={result.sub_score_delete_unread} | "
              f"freq={result.sub_score_frequency}")
        print(f"   Action     : {result.recommended_action}")
        print(f"   🔍 {result.explanation}")

        # Nếu CRITICAL → kích hoạt Ethical UX
        handle_ethical_ux_trigger(result)

    print("\n" + "=" * 60)
    print("  Simulation hoàn tất.")
    print("=" * 60)
