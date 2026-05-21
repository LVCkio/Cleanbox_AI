# 🌱 CleanInbox AI — MVP Technical Documentation

> **SaaS Middleware** tối ưu hóa Email Marketing & giảm rác thải kỹ thuật số  
> Plug-and-play API · Mailchimp · HubSpot · SendGrid · ESG Reporting

---

## 📁 Cấu trúc dự án

```
cleanbox_ai/
├── docs/
│   └── database_schema.md          # Schema PostgreSQL (7 bảng)
├── fatigue_intelligence/
│   └── bfs_calculator.py           # ⭐ Bộ não AI — Tính BFS
├── ethical_ux/
│   └── popup.html                  # Widget "Chia tay văn minh"
├── esg_dashboard/
│   └── dashboard.html              # Dashboard CO2 & ESG
└── README.md
```

---

## 🧩 4 Module Cốt Lõi

### Module 1 — API Gateway
- Kết nối Mailchimp / HubSpot / SendGrid qua OAuth2 + API Key
- Đồng bộ danh sách contact và campaign metadata
- Schema: bảng `api_connections` (mã hóa AES-256)

### Module 2 — Fatigue Intelligence (AI Brain)
**File:** `fatigue_intelligence/bfs_calculator.py`

```
BFS = 0.30 × S_time + 0.45 × S_delete + 0.25 × S_freq
```

| Đầu vào | Trọng số | Ý nghĩa |
|---------|---------|---------|
| `time_spent_seconds` | 30% | Thời gian đọc email |
| `consecutive_unread_deletes` | 45% | Xóa không đọc liên tiếp |
| `received_frequency_per_week` | 25% | Tần suất nhận thư |

**Ngưỡng hành động:**
| BFS | Risk Level | Hành động |
|-----|-----------|-----------|
| 1–40 | 🟢 LOW | Giữ nguyên chiến lược |
| 41–65 | 🟡 MEDIUM | Giảm tần suất gửi |
| 66–80 | 🟠 HIGH | Gửi email giữ chân |
| **81–100** | **🔴 CRITICAL** | **→ Kích hoạt Ethical UX Popup** |

### Module 3 — Ethical UX Manager
**File:** `ethical_ux/popup.html`
- Popup "Chia tay văn minh" khi BFS > 80
- Snooze: 30 / 60 / 90 ngày
- Unsubscribe hoàn toàn
- Tuân thủ Nghị định 13/2023/NĐ-CP

### Module 4 — ESG Reporter
**File:** `esg_dashboard/dashboard.html`
- Tổng email lọc + chi phí tiết kiệm ($0.02/email)
- CO2 tiết kiệm (0.3g/email) → tự chuyển đổi g/kg/tấn
- Progress bar tiến độ mục tiêu 1.5 tấn CO2/năm
- Biểu đồ cột 6 tháng + nút xuất báo cáo JSON

---

## 🗄️ Database (PostgreSQL)

7 bảng chính: `organizations` → `api_connections` → `contacts` → `micro_behaviors` → `brand_fatigue_scores` → `campaigns` → `esg_co2_tracking`

Chi tiết: xem [`docs/database_schema.md`](docs/database_schema.md)

---

## 🚀 Chạy Demo

```bash
# Module 2 — BFS Calculator (yêu cầu Python 3.8+)
python fatigue_intelligence/bfs_calculator.py

# Module 3 & 4 — Mở trực tiếp bằng trình duyệt
# Không cần server, chạy được offline
open ethical_ux/popup.html
open esg_dashboard/dashboard.html
```

---

## 📊 KPI Kỳ Vọng

| Chỉ số | Mục tiêu |
|--------|---------|
| Open Rate | +40% |
| Giảm chi phí data ảo | -20% |
| CO2 cắt giảm năm đầu | ≥ 1.5 tấn |
| Thời gian tích hợp API | ≤ 15 phút |

---

## ⚖️ Tuân thủ Pháp lý
- **Nghị định 13/2023/NĐ-CP** (PDPA Việt Nam): Lưu trạng thái consent, mã hóa dữ liệu cá nhân
- **GHG Protocol Scope 3** — Category 11: Chuẩn đo CO2 quốc tế
- **ESG Net Zero 2050**: Lộ trình báo cáo phát triển bền vững
