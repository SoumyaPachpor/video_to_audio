#!/usr/bin/env bash

# Install FFmpeg
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar xJ
mv ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/
mv ffmpeg-*-amd64-static/ffprobe /usr/local/bin/

# Proceed with app setup
pip install -r requirements.txt
