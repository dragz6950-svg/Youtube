from flask import Flask, request, jsonify
import subprocess
import os
import uuid
import imageio_ffmpeg
import requests

app = Flask(__name__)
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

@app.route('/process', methods=['POST'])
def process_video():
    data = request.json
    video_url = data.get('video_url')
    title = data.get('title', 'video')

    unique_id = str(uuid.uuid4())[:8]
    raw_path = f"/tmp/{unique_id}_raw.mp4"
    edited_path = f"/tmp/{unique_id}_edited.mp4"

    # Download video from Pexels
    response = requests.get(video_url, stream=True)
    with open(raw_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Edit with FFmpeg (flip + speed)
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
        'title': title
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
