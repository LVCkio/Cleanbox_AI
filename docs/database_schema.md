# CleanInbox AI — Database Schema (PostgreSQL)

## Tổng quan kiến trúc dữ liệu

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   organizations  │────<│  api_connections  │     │      campaigns      │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
         │                                                   │
         │                                                   │
         ▼                                                   ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│    contacts     │────<│ micro_behaviors  │     │   esg_co2_tracking  │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  brand_fatigue_scores   │
└─────────────────────────┘
```

---

## 1. Bảng `organizations` — Doanh nghiệp

```sql
CREATE TABLE organizations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    plan            VARCHAR(50) DEFAULT 'starter',  -- starter | pro | enterprise
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 2. Bảng `api_connections` — Kết nối API bên thứ 3

```sql
CREATE TABLE api_connections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID REFERENCES organizations(id) ON DELETE CASCADE,
    provider        VARCHAR(50) NOT NULL,           -- 'mailchimp' | 'hubspot' | 'sendgrid'
    api_key_hash    TEXT NOT NULL,                  -- SHA-256 hash, không lưu raw key
    access_token    TEXT,                           -- OAuth token (encrypted AES-256)
    status          VARCHAR(20) DEFAULT 'active',   -- active | expired | revoked
    last_synced_at  TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 3. Bảng `contacts` — Danh sách khách hàng cuối

```sql
CREATE TABLE contacts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id              UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email               VARCHAR(255) NOT NULL,
    -- Tuân thủ Nghị định 13/2023/NĐ-CP: lưu trạng thái đồng ý
    consent_status      VARCHAR(20) DEFAULT 'active', -- active | snoozed | unsubscribed
    consent_given_at    TIMESTAMPTZ,
    snooze_until        TIMESTAMPTZ,               -- NULL nếu không snooze
    snooze_days         INTEGER,                   -- 30 | 60 | 90
    -- Metadata hành vi tổng hợp
    total_emails_received   INTEGER DEFAULT 0,
    total_emails_opened     INTEGER DEFAULT 0,
    total_emails_deleted_unread INTEGER DEFAULT 0,
    -- Trạng thái cảnh báo
    ethical_ux_flag     BOOLEAN DEFAULT FALSE,     -- TRUE = kích hoạt Ethical UX popup
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(org_id, email)
);
```

---

## 4. Bảng `micro_behaviors` — Hành vi vi mô (Mỗi lần tương tác)

```sql
CREATE TABLE micro_behaviors (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id                  UUID REFERENCES contacts(id) ON DELETE CASCADE,
    campaign_id                 UUID,              -- FK đến campaigns nếu có
    event_type                  VARCHAR(50),       -- 'open' | 'delete_unread' | 'click' | 'spam'
    time_spent_seconds          INTEGER DEFAULT 0, -- Thời gian đọc email (giây)
    scroll_depth_percent        FLOAT,             -- % cuộn nội dung email (0–100)
    device_type                 VARCHAR(30),       -- 'mobile' | 'desktop' | 'tablet'
    recorded_at                 TIMESTAMPTZ DEFAULT NOW()
);
-- Index để query nhanh theo contact và thời gian
CREATE INDEX idx_micro_behaviors_contact ON micro_behaviors(contact_id, recorded_at DESC);
```

---

## 5. Bảng `brand_fatigue_scores` — Điểm mệt mỏi thương hiệu

```sql
CREATE TABLE brand_fatigue_scores (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id          UUID REFERENCES contacts(id) ON DELETE CASCADE,
    org_id              UUID REFERENCES organizations(id),
    bfs_score           FLOAT NOT NULL CHECK (bfs_score BETWEEN 1 AND 100),
    -- Thành phần điểm chi tiết để debug / audit
    score_time_spent    FLOAT,
    score_delete_unread FLOAT,
    score_frequency     FLOAT,
    risk_level          VARCHAR(20),   -- 'low' | 'medium' | 'high' | 'critical'
    action_triggered    VARCHAR(50),   -- 'none' | 'ethical_ux_popup' | 'snooze' | 'unsubscribe'
    calculated_at       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_bfs_contact ON brand_fatigue_scores(contact_id, calculated_at DESC);
```

---

## 6. Bảng `campaigns` — Chiến dịch email

```sql
CREATE TABLE campaigns (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name            VARCHAR(255),
    provider        VARCHAR(50),           -- mailchimp | hubspot | sendgrid
    provider_ref_id VARCHAR(255),          -- ID chiến dịch bên thứ 3
    sent_at         TIMESTAMPTZ,
    total_sent      INTEGER DEFAULT 0,
    total_filtered  INTEGER DEFAULT 0,     -- Số email đã bị lọc/không gửi
    status          VARCHAR(30) DEFAULT 'draft'
);
```

---

## 7. Bảng `esg_co2_tracking` — Theo dõi CO2 tiết kiệm

```sql
CREATE TABLE esg_co2_tracking (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id              UUID REFERENCES organizations(id),
    campaign_id         UUID REFERENCES campaigns(id),
    emails_filtered     INTEGER NOT NULL DEFAULT 0,
    -- CO2 = emails_filtered * 0.3g
    co2_saved_grams     FLOAT GENERATED ALWAYS AS (emails_filtered * 0.3) STORED,
    cost_saved_usd      FLOAT GENERATED ALWAYS AS (emails_filtered * 0.02) STORED,
    period_start        DATE,
    period_end          DATE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Tóm tắt quan hệ

| Bảng | Mô tả | Quan hệ chính |
|------|-------|---------------|
| `organizations` | Doanh nghiệp SaaS client | Root entity |
| `api_connections` | API key Mailchimp/HubSpot/SendGrid | N:1 org |
| `contacts` | Người nhận email cuối | N:1 org |
| `micro_behaviors` | Từng sự kiện hành vi | N:1 contact |
| `brand_fatigue_scores` | Điểm BFS tính định kỳ | N:1 contact |
| `campaigns` | Chiến dịch email | N:1 org |
| `esg_co2_tracking` | CO2 + chi phí tiết kiệm | N:1 campaign |
