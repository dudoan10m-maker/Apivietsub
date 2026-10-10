# VietSub AI V4 — cấu trúc đã sửa để deploy Render

## Cấu trúc
Đưa các file trong ZIP vào **root của repository**:
- `app.py`
- `requirements.txt`
- `render.yaml`
- `templates/index.html`

Không để nguyên một thư mục `vietsub_ai_starter/` lồng bên trong nếu Render đang chạy lệnh từ root repository.

## Render
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`
- Environment: thêm `OPENAI_API_KEY` làm key, giá trị là API key mới của bạn.
- Sau khi lưu Environment, đợi deploy hoàn tất rồi kiểm tra `/health`.

## Kiểm tra
`/health` trả `ok: true` nghĩa là Flask chạy được.
`openai_api_key_configured: true` chỉ có nghĩa là biến môi trường được đọc, **không** có nghĩa pipeline dịch video đã sẵn sàng.

## Giới hạn cần biết
Đây vẫn là bản khung giao diện + upload. Chưa tích hợp pipeline ASR/transcription, dịch, TTS, FFmpeg và xuất video thực tế. Nút xử lý hiện sẽ trả `needs_configuration`, không tạo ra video dịch hoàn chỉnh. Không nên quảng cáo/cho rằng tính năng dịch thật đã hoạt động cho tới khi bổ sung và kiểm thử pipeline đó.
