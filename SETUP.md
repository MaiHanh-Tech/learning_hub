# Hướng dẫn cài đặt & deploy Cognitive Weaver

App này **chạy được ngay với các file trong repo**, nhưng cần 2 thứ bên ngoài
mà đúng ra không nên (và không thể) đóng gói sẵn trong code: **API key** và
**bảng dữ liệu Supabase**. Thiếu 2 thứ này, app vẫn khởi động được (mọi lỗi
kết nối đều được try/except bắt lại rồi âm thầm vô hiệu hoá tính năng liên
quan), nhưng đăng nhập / lưu lịch sử / gọi AI sẽ không hoạt động mà không có
thông báo lỗi rõ ràng.

## 1. Cài thư viện

```bash
pip install -r requirements.txt
```

## 2. Khai báo secrets

Sao chép `.streamlit/secrets.toml.example` thành `.streamlit/secrets.toml`
rồi điền giá trị thật (xem chi tiết từng key trong file mẫu). Nếu deploy trên
Streamlit Community Cloud: dán nội dung đã điền vào **App settings → Secrets**
thay vì tạo file.

**Tối thiểu cần có** để app hoạt động đầy đủ:
- `[supabase] url`, `key` — đăng nhập + lưu lịch sử (Tab "Nhật Ký")
- `admin_password_hash` — mật khẩu admin dự phòng khi Supabase lỗi
- `[api_keys] gemini_api_key` — bắt buộc, vì đây là engine AI chính (ưu tiên
  số 1 trong `ai_core.py`). `deepseek`/`xai` chỉ là fallback, không bắt buộc.

## 3. Tạo bảng trong Supabase

Vào Supabase → SQL Editor, chạy:

```sql
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  username text unique not null,
  password_hash text not null,
  role text not null default 'user',
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists history_logs (
  id uuid primary key default gen_random_uuid(),
  type text,
  title text,
  content text,
  user_name text,
  sentiment_score numeric default 0,
  sentiment_label text default 'Neutral',
  created_at timestamptz not null default now()
);
```

Chưa cần tạo `user_profiles` / `user_interactions` — 2 bảng này chỉ phục vụ
tính năng `PersonalRAG` (`services/blocks/personal_rag_system.py`), hiện
**chưa được nối vào giao diện** (xem mục 5).

## 4. Chạy thử local

```bash
streamlit run app.py
```

Đăng nhập lần đầu bằng mật khẩu ứng với `admin_password_hash` đã khai báo
(đây là tài khoản "SuperAdmin" cứng, không nằm trong bảng `users`). Sau đó có
thể vào Admin Panel ở sidebar để tạo thêm user thường qua bảng `users`.

## 5. Việc còn treo — cần quyết định, không phải bug

- **`PersonalRAG`** (`services/blocks/personal_rag_system.py`): tính năng
  ghi nhớ phong cách tư duy người dùng qua các lần tương tác — đã code xong,
  chưa nối vào UI nào. Cần bảng `user_profiles`, `user_interactions` nếu
  muốn bật.
- **`bot.py`**: bot Telegram độc lập, KHÔNG chạy chung với app Streamlit này.
  Cài riêng bằng `pip install -r requirements-bot.txt`, chạy `python bot.py`,
  cần `TELEGRAM_TOKEN` + `GOOGLE_API_KEY` ở biến môi trường.
