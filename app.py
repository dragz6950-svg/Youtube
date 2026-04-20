from flask import Flask, request, jsonify
import yt_dlp
import subprocess
import os
import uuid
import imageio_ffmpeg

app = Flask(__name__)
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

@app.route('/process', methods=['POST'])
def process_video():
    data = request.json
    video_id = data.get('video_id')
    title = data.get('title', 'video')
    
    unique_id = str(uuid.uuid4())[:8]
    raw_path = f"/tmp/{unique_id}_raw.mp4"
    edited_path = f"/tmp/{unique_id}_edited.mp4"

    ydl_opts = {
        'format': 'mp4',
        'outtmpl': raw_path,
        'quiet': True,
        'extractor_args': {'youtube': {'player_client': ['android']}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36'
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

    subprocess.run([
        ffmpeg_path, '-i', raw_path,
        '-vf', 'hflip',
        '-c:v', 'libx264', '-c:a', 'aac',
        edited_path
    ])

    os.remove(raw_path)

    return jsonify({
        'status': 'success',
        'edited_path': edited_path,
        'video_id': video_id,
        'title': title
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
