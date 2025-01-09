from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import os
import subprocess
import sys
from pathlib import Path
from threading import Thread
import time

app = Flask(__name__)
CORS(app)

# Store download progress
download_status = {}

port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)


def check_ffmpeg():
    """Check if FFmpeg is installed and install it if missing."""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        print("FFmpeg not found. Please install FFmpeg manually.")
        return False

def download_audio(video_url, output_folder="downloads"):
    """Download a single YouTube video as MP3."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    download_status[video_url] = {
        'progress': 0,
        'status': 'downloading',
        'filename': None,
        'error': None,
        'title': None
    }

    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                download_status[video_url]['progress'] = float(d['_percent_str'].replace('%', ''))
            except:
                pass
        elif d['status'] == 'finished':
            download_status[video_url]['status'] = 'converting'
            download_status[video_url]['filename'] = os.path.basename(d['filename'])

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_status[video_url]['title'] = info.get('title', 'Unknown Title')
            ydl.download([video_url])
        download_status[video_url]['status'] = 'completed'
    except Exception as e:
        download_status[video_url]['status'] = 'error'
        download_status[video_url]['error'] = str(e)

@app.route('/')
def home():
    return "Backend is live and working!"

@app.route('/api/download', methods=['POST'])
def download():
    data = request.get_json()
    video_url = data.get('url')
    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    # Start download in background
    Thread(target=download_audio, args=(video_url,), daemon=True).start()
    return jsonify({'status': 'Download started', 'url': video_url})

@app.route('/api/status/<path:url>')
def status(url):
    if url in download_status:
        return jsonify(download_status[url])
    return jsonify({'status': 'not_found'})

@app.route('/api/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory('downloads', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
