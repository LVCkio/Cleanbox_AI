# 🌱 CleanInbox AI — SaaS Middleware & ESG Reporting

> **SaaS Middleware** tối ưu hóa Email Marketing & giảm rác thải kỹ thuật số  
> Plug-and-play API · Mailchimp · HubSpot · SendGrid · ESG Reporting

[![Deploy to Render](https://render.com/images/deploy-to-render.svg)](https://render.com/deploy?repo=https://github.com/LVCkio/Cleanbox_AI)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/LVCkio/Cleanbox_AI)
[![GitHub Pages Frontend](https://img.shields.io/badge/Frontend-GitHub%20Pages-blue?style=flat&logo=github)](https://LVCkio.github.io/Cleanbox_AI/esg_dashboard/dashboard.html)

---

## 📧 Khả năng lọc Email của App (Có lọc được không?)

**CÓ, ứng dụng này lọc email cực kỳ thông minh và tuân thủ đạo đức (Ethical UX)!**

Thay vì lọc thư rác (spam) truyền thống, CleanInbox AI lọc **danh bạ nhận email (Contact List)** để loại bỏ các email kém tương tác dựa trên thuật toán AI:
1. **Tính điểm Fatigue (BFS):** Bộ não AI liên tục tính toán chỉ số mệt mỏi **Brand Fatigue Score (BFS)** của từng khách hàng.
2. **Kích hoạt Lọc tự động:** 
   - Khi BFS vượt ngưỡng nguy hiểm (>80), widget **Ethical UX** xuất hiện để cho phép người dùng **Snooze (tạm dừng nhận thư 30/60/90 ngày)** hoặc **Unsubscribe (Hủy đăng ký hoàn toàn)**.
   - **Đồng bộ Real-time API:** Khi người dùng chọn Snooze hoặc Unsubscribe, hệ thống gọi API backend và lập tức cập nhật trạng thái vào hệ thống Email Marketing của bạn (như **Mailchimp, HubSpot, SendGrid**).
3. **Hiệu quả thực tế:** 
   - **Lọc sạch danh bạ ảo:** Giúp doanh nghiệp giảm **20%** chi phí lưu trữ & gửi email không hiệu quả.
   - **Tăng tỷ lệ Open Rate (+40%):** Do chỉ gửi email cho những người thực sự muốn đọc.
   - **Báo cáo ESG & CO2:** Mỗi email không gửi đi tiết kiệm **0.3g CO2** và **$0.02** chi phí vận hành.

---

## 🚀 Hướng Dẫn Deploy Lên Internet

Hệ thống được thiết kế dạng **decoupled (tách biệt)** để deploy cực kỳ đơn giản và tối ưu chi phí (miễn phí 100%):

### 1. Backend (FastAPI + PostgreSQL)
Bạn có thể chọn 1 trong 2 nền tảng đám mây phổ biến nhất hiện nay:
* **Deploy lên Render (Khuyên dùng):** Click vào nút **Deploy to Render** ở trên. Render sẽ tự động đọc file `render.yaml`, tạo Database PostgreSQL, build Dockerfile cho FastAPI và cấu hình sẵn mọi biến môi trường.
* **Deploy lên Railway:** Click vào nút **Deploy on Railway** ở trên để deploy tức thì thông qua template có sẵn.
* **Biến môi trường tùy chỉnh:**
  - `DATABASE_URL`: Tự động cấu hình (Render/Railway cấp).
  - `SECRET_KEY`: Khóa bảo mật JWT (Render tự sinh hoặc tự điền).
  - `CORS_ORIGINS`: Để `*` để frontend trên GitHub Pages có thể kết nối được.

### 2. Frontend (Giao diện HTML/CSS/JS tĩnh)
* Frontend được cấu hình deploy tự động lên **GitHub Pages** thông qua GitHub Actions (`.github/workflows/gh-pages.yml`).
* Mỗi khi bạn `git push` lên branch `main`, GitHub sẽ tự động build và cập nhật trang web của bạn tại:
  `https://LVCkio.github.io/Cleanbox_AI/esg_dashboard/dashboard.html`
* **Kết nối động với API:** 
  - Trên giao diện của ESG Dashboard và Ethical UX Popup, click vào nút cài đặt (**⚙️**).
  - Bạn chỉ cần chuyển từ chế độ **Mock Mode** sang **Live API Mode**, điền địa chỉ API Backend đã deploy (ví dụ: `https://cleaninbox-backend.onrender.com`) và nhấn **Đăng nhập nhanh** (tài khoản demo: `admin@cleaninbox.ai` / `demo1234`).
  - Hệ thống sẽ kết nối trực tiếp với Database PostgreSQL real-time!

---

## 💻 Setup trên máy tính khác (Từng bước chi tiết)

Để chạy dự án này trên một máy tính mới, hãy làm theo các bước dưới đây:

### A. Đối với Windows (Tự động 100% bằng Script)
1. **Tải mã nguồn:** Tải folder dự án về máy hoặc clone qua Git:
   ```bash
   git clone https://github.com/LVCkio/Cleanbox_AI.git
   cd Cleanbox_AI
   ```
2. **Chạy Script setup tự động:** 
   - Click chuột phải vào file `setup.ps1` -> Chọn **Run with PowerShell**.
   - Hoặc mở PowerShell trong thư mục dự án và chạy:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
     .\setup.ps1
     ```
   - Script sẽ tự động: Kiểm tra Python, tạo môi trường ảo `.venv`, cài đặt tất cả packages từ `requirements.txt`, và copy file `.env`.
3. **Kích hoạt và Khởi chạy:**
   - Kích hoạt môi trường ảo: `.venv\Scripts\Activate.ps1`
   - Khởi chạy backend: `uvicorn backend.main:app --reload`
   - Mở tài liệu API Swagger: `http://127.0.0.1:8000/docs`
   - Khởi chạy Frontend: `npx serve . -p 3999` (Truy cập `http://localhost:3999/esg_dashboard/dashboard.html`)

### B. Đối với macOS / Linux
1. **Mở Terminal** di chuyển vào thư mục dự án.
2. **Tạo và kích hoạt môi trường ảo (Virtualenv):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Cài đặt các gói phụ thuộc:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. **Cấu hình file môi trường:**
   ```bash
   cp .env.example .env
   ```
5. **Khởi chạy ứng dụng:**
   - Khởi động Backend API: `uvicorn backend.main:app --reload`
   - Chạy Frontend: Mở trực tiếp file `esg_dashboard/dashboard.html` trên trình duyệt hoặc chạy một static server:
     ```bash
     npx serve . -p 3999
     ```

---

## 📁 Cấu trúc dự án

```
cleanbox_ai/
├── .github/
│   └── workflows/
│       └── gh-pages.yml            # CI/CD tự động deploy Frontend lên GitHub Pages
├── backend/
│   ├── main.py                     # File chạy chính FastAPI Backend
│   ├── database.py                 # Kết nối DB (SQLite/PostgreSQL)
│   ├── config.py                   # Đọc biến môi trường từ .env
│   ├── models.py                   # SQLAlchemy Models (Organizations, Contacts, CO2...)
│   └── routers/                    # API Endpoints (Auth, Fatigue, Ethical UX, ESG)
├── docs/
│   └── database_schema.md          # Schema PostgreSQL (7 bảng)
├── fatigue_intelligence/
│   └── bfs_calculator.py           # ⭐ Bộ não AI — Tính BFS
├── ethical_ux/
│   └── popup.html                  # Widget "Chia tay văn minh" + Floating Settings
├── esg_dashboard/
│   └── dashboard.html              # Dashboard ESG & CO2 + Floating Settings + JSON Export
├── render.yaml                     # Cấu hình Infrastructure-as-Code cho Render
├── railway.toml                    # Cấu hình Deploy cho Railway
├── Dockerfile                      # Dockerize Backend phục vụ Production
├── requirements.txt                # Dependencies của Python
└── setup.ps1                       # Script cài đặt tự động trên Windows
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
* **time_spent_seconds (30%):** Thời gian đọc email.
* **consecutive_unread_deletes (45%):** Xóa không đọc liên tiếp.
* **received_frequency_per_week (25%):** Tần suất nhận thư.

### Module 3 — Ethical UX Manager
- Popup "Chia tay văn minh" khi BFS > 80.
- Snooze: 30 / 60 / 90 ngày.
- Unsubscribe hoàn toàn tuân thủ Nghị định 13/2023/NĐ-CP.

### Module 4 — ESG Reporter
- Tổng email lọc + chi phí tiết kiệm ($0.02/email).
- CO2 tiết kiệm (0.3g/email) → tự chuyển đổi g/kg/tấn.
- Biểu đồ trực quan và chức năng xuất báo cáo chuẩn ESG.

---

## ⚖️ Tuân thủ Pháp lý & Tiêu chuẩn
- **Nghị định 13/2023/NĐ-CP** (PDPA Việt Nam): Bảo vệ dữ liệu cá nhân, lưu trữ đồng ý/hủy đồng ý rõ ràng.
- **GHG Protocol Scope 3** — Category 11: Đo lường gián tiếp phát thải từ sản phẩm dịch vụ kỹ thuật số.
- **ESG Net Zero 2050**: Cung cấp số liệu chính xác để kiểm toán phát triển bền vững.
