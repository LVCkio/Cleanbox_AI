-- CleanInbox AI — PostgreSQL Init Script
-- Chạy tự động khi container DB khởi tạo lần đầu

-- Kích hoạt extension UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tạo index cho performance
-- (Các bảng được SQLAlchemy tạo, indexes bổ sung tạo ở đây)
