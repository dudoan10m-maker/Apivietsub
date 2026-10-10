# VietSub AI — bộ khung khởi đầu

## Có gì trong bản này?
- Giao diện neon responsive, dùng được trên Android.
- Chọn video từ thiết bị và xem trước trong trình duyệt.
- Kiểm tra video dài tối đa 1 tiếng ở phía giao diện.
- AI tự động nhận diện ngôn ngữ gốc; người dùng chỉ cần chọn ngôn ngữ đích, kiểu giọng, phụ đề, âm lượng và chất lượng.
- Flask backend có `/health`, nhận upload và API album đầu ra.
- Nút chính tải video lên rồi gửi các cài đặt ngôn ngữ, giọng, âm lượng và chất lượng đến backend.
- Khu vực tải về chỉ hiện khi backend trả trạng thái hoàn tất và đường dẫn file.

## Quan trọng
Đây chưa phải hệ thống dịch/lồng tiếng hoàn chỉnh. Endpoint `/api/jobs/<id>/start` trả về HTTP 501 có chủ đích để không giả vờ đã dịch video. Muốn xử lý thực tế cần tích hợp:
1. ASR (nhận dạng lời thoại và timestamp)
2. Dịch máy đa ngôn ngữ
3. TTS (tạo giọng đọc ở ngôn ngữ đích)
4. FFmpeg (ghép phụ đề, trộn âm thanh, xuất video)
5. Hàng đợi nền và lưu trữ bền vững cho video dài

## Chạy thử trên Android bằng Termux
```bash
pkg update
pkg install python -y
pip install -r requirements.txt
python app.py
```
Mở `http://127.0.0.1:5000` trong trình duyệt trên điện thoại.

## Deploy Render
1. Đẩy toàn bộ thư mục này lên GitHub.
2. Tạo Web Service trên Render, chọn repo.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`
5. Kiểm tra `https://TEN-MIEN.onrender.com/health`
6. Trong Render → **Environment**, thêm biến `OPENAI_API_KEY` và dán API key mới của mày vào ô Value (không ghi key vào GitHub/app.py). Sau đó redeploy. `/health` sẽ báo `openai_api_key_configured: true` nếu biến đã được nhận.

## Giới hạn cần biết
- Giới hạn upload được đặt ở 2 GB trong Flask, nhưng Render/proxy và dung lượng đĩa có thể có giới hạn thấp hơn.
- Render filesystem thường không nên được dùng làm kho lưu trữ video lâu dài; dùng object storage cho sản phẩm thực tế.
- Video dài 1 tiếng có thể tốn nhiều thời gian và chi phí xử lý. Chưa nên công khai cho người dùng thật trước khi thêm giới hạn, xác thực, xóa file tự động và worker.
- Tùy chọn 4K chỉ là lựa chọn giao diện cho đến khi pipeline FFmpeg và nguồn video hỗ trợ.

## Bảo mật API key
- Không đưa API key vào HTML, ảnh chụp màn hình, GitHub hoặc file ZIP công khai.
- Nếu key đã bị gửi trong chat hoặc nơi công khai, hãy revoke key đó và tạo key mới.
- Bản này mới đọc biến `OPENAI_API_KEY` để kiểm tra cấu hình; pipeline nhận dạng giọng nói/dịch/TTS chưa được tích hợp hoàn chỉnh.
