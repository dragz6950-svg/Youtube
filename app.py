from flask import Flask, request, jsonify
import yt_dlp
import subprocess
import os
import uuid

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_video():
    data = request.json
    video_id = data.get('video_id')
    title = data.get('title', 'video')
    
    unique_id = str(uuid.uuid4())[:8]
    raw_path = f"/tmp/{unique_id}_raw.mp4"
    edited_path = f"/tmp/{unique_id}_edited.mp4"

    # Download video
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': raw_path,
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

    # Edit video with FFmpeg (speed up, flip, color filter)
    subprocess.run([
        'ffmpeg', '-i', raw_path,
        '-vf', 'hflip,colorchannelmixer=1.1:0:0:0:0:1.1:0:0:0:0:1.1:0',
        '-filter:v', 'setpts=0.95*PTS',
        '-filter:a', 'atempo=1.05',
        '-c:v', 'libx264', '-c:a', 'aac',
        edited_path
    ])

    # Cleanup raw
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
    app.run(host='0.0.0.0', port=5000)
