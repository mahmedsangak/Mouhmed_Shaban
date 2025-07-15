from flask import Flask, render_template, request, send_file
from gtts import gTTS
from pydub import AudioSegment
import os
import io

app = Flask(__name__)

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    page = request.form.get("page", "").strip()
    unit = request.form.get("unit", "").strip()
    part = request.form.get("part", "").strip()
    item = request.form.get("item", "").strip()
    speed = float(request.form.get("speed", "1.0"))
    answers = request.form.getlist("answers[]")

    combined = AudioSegment.silent(duration=0)
    silence = AudioSegment.silent(duration=400)

    index = 0
    if page:
        combined += silence + text_to_speech(f"Page: {page}", f"{TEMP_DIR}/page_{index}.mp3", speed)
        index += 1

    if unit:
        combined += silence + text_to_speech(unit, f"{TEMP_DIR}/unit_{index}.mp3", speed)
        index += 1

    if part:
        combined += silence + text_to_speech(part, f"{TEMP_DIR}/part_{index}.mp3", speed)
        index += 1

    if item:
        combined += silence + text_to_speech(item, f"{TEMP_DIR}/item_{index}.mp3", speed)
        index += 1

    for i, ans in enumerate(answers):
        if ans.strip():
            combined += silence + text_to_speech(f"{i + 1}: {ans}", f"{TEMP_DIR}/ans_{i}.mp3", speed)

    output_file = io.BytesIO()
    combined.export(output_file, format="mp3")
    output_file.seek(0)

    for file in os.listdir(TEMP_DIR):
        os.remove(os.path.join(TEMP_DIR, file))

    return send_file(
        output_file,
        mimetype="audio/mpeg",
        as_attachment=True,
        download_name="answers.mp3"
    )

def text_to_speech(text, filename, speed="1.0"):
    lang = "ar" if any('\u0600' <= c <= '\u06FF' for c in text) else "en"
    slow = float(speed) < 0.99
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save(filename)
    return AudioSegment.from_mp3(filename)

if __name__ == "__main__":
    app.run(debug=True)
