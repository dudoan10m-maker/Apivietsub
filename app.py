import os, uuid, json, time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Keep API keys in environment variables (Render Dashboard > Environment), never in source code.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()

BASE = Path(__file__).resolve().parent
UPLOAD_DIR = BASE / "uploads"
OUTPUT_DIR = BASE / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024  # 2 GB upload cap; host may impose a lower limit
ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm", "m4v"}
jobs = {}

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "service": "VietSub AI starter",
        "openai_api_key_configured": bool(OPENAI_API_KEY),
        "translation_engine": "not_configured",
    })

@app.post("/api/upload")
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "Chưa nhận được file video."}), 400
    file = request.files["video"]
    if not file.filename:
        return jsonify({"error": "Hãy chọn video cần dịch."}), 400
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Định dạng chưa hỗ trợ. Dùng MP4, MOV, AVI, MKV, WEBM hoặc M4V."}), 400
    job_id = uuid.uuid4().hex[:12]
    filename = secure_filename(file.filename) or f"video.{ext}"
    stored_name = f"{job_id}_{filename}"
    path = UPLOAD_DIR / stored_name
    file.save(path)
    job = {
        "id": job_id, "filename": filename, "stored_name": stored_name,
        "size": path.stat().st_size, "status": "uploaded",
        "progress": 0, "message": "Video đã tải lên. Cần cấu hình engine AI để dịch và lồng tiếng.",
        "created_at": int(time.time()), "output": None
    }
    jobs[job_id] = job
    return jsonify(job), 201

@app.post("/api/jobs/<job_id>/start")
def start_job(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Không tìm thấy video. Có thể server đã khởi động lại."}), 404
    # The UI can submit translation settings, but real processing requires configured ASR/translation/TTS/FFmpeg providers.
    settings = request.get_json(silent=True) or {}
    job["settings"] = {
        "source_lang": "auto",
        "target_lang": settings.get("target_lang", "Tiếng Việt"),
        "voice": settings.get("voice", "Nữ — tự nhiên"),
        "subtitle_mode": settings.get("subtitle_mode", "Phụ đề + lồng tiếng"),
        "original_volume": settings.get("original_volume", 70),
        "dub_volume": settings.get("dub_volume", 100),
        "quality": settings.get("quality", "1080p"),
    }
    job["status"] = "needs_configuration"
    job["message"] = "Video đã tải lên cùng cài đặt. Chưa thể xử lý vì chưa cấu hình engine AI."
    return jsonify({
        "id": job_id,
        "status": "needs_configuration",
        "progress": 0,
        "message": "Video đã tải lên cùng cài đặt. Để dịch và xuất file thật, cần cấu hình engine nhận dạng giọng nói, dịch thuật, TTS và FFmpeg."
    }), 200

@app.get("/api/jobs/<job_id>")
def get_job(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Không tìm thấy tác vụ."}), 404
    return jsonify(job)

@app.get("/api/album")
def album():
    items = []
    for p in sorted(OUTPUT_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.is_file():
            items.append({"name": p.name, "url": f"/outputs/{p.name}", "size": p.stat().st_size})
    return jsonify(items)

@app.get("/outputs/<path:filename>")
def output_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": "Video vượt giới hạn upload của server. Hãy tăng giới hạn hoặc dùng lưu trữ ngoài."}), 413

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
