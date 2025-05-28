#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import subprocess
import librosa
import numpy as np
import csv
import time
from PIL import Image
import imagehash

video_screen = "screen_recording.webm"
audio_file = "audio_recording.webm"

# 1. Extract audio for analysis
def extract_audio(video_path, audio_path):
    print(f"📌 [提取音频] {video_path} -> {audio_path}")
    command = ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"]
    subprocess.run(command)

# 2. Calculate audio peak timestamps
def get_audio_peaks(audio_path, sr=22050):
    print(f"📌 [分析音频] 计算音频峰值: {audio_path}")
    y, sr = librosa.load(audio_path, sr=sr)
    rms = librosa.feature.rms(y=y)[0]
    peaks = np.where(rms > np.percentile(rms, 90))[0]
    return librosa.frames_to_time(peaks, sr=sr)

# 3. Simulate recording of mouse clicks（空实现保留结构）
def record_mouse_clicks(video_path, csv_path):
    print(f"📌 [记录鼠标点击] 监听中... (按 'q' 退出)")
    video_start_time = time.time()
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['relative_timestamp'])
        # 可选手动添加模拟点击： writer.writerow([12.5])

# 4. Get mouse click times (CSV)
def get_mouse_click_times(csv_path):
    if not os.path.exists(csv_path):
        return np.array([])
    with open(csv_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        return np.array([float(row[0]) for row in reader if row])

# 5. Get timestamps of frames with drastic visual changes
def get_visual_change_times(video_path, threshold=0.5, frame_rate=1, save_folder="visual_changes"):
    print(f"📌 [图像变化检测] 分析中: {video_path}")
    temp_folder = "temp_frames"
    os.makedirs(temp_folder, exist_ok=True)
    os.makedirs(save_folder, exist_ok=True)

    # Extract frames
    command = [
        "ffmpeg", "-i", video_path, "-vf", f"fps={frame_rate}",
        os.path.join(temp_folder, "frame_%04d.jpg"), "-hide_banner", "-loglevel", "error", "-y"
    ]
    subprocess.run(command)

    # Analyse frame hash differences
    timestamps = []
    prev_hash = None
    for i, fname in enumerate(sorted(os.listdir(temp_folder))):
        img_path = os.path.join(temp_folder, fname)
        with Image.open(img_path) as img:
            img_hash = imagehash.phash(img)

        if prev_hash is not None:
            diff = (prev_hash - img_hash) / len(img_hash.hash) ** 2
            if diff >= threshold:
                save_path = os.path.join(save_folder, fname)
                img.save(save_path)
                timestamps.append(i / frame_rate)

        prev_hash = img_hash

    print(f"✅ [图像变化检测] 共检测到 {len(timestamps)} 个高变化帧，已保存至 {save_folder}")
    return np.array(timestamps)

# 6. Merge timestamps and select keyframes (deinterlacing)
def get_final_key_frames(audio_peaks, mouse_clicks, visual_changes, min_gap=20, max_clips=10):
    print(f"📌 [选择关键帧] 计算中...")
    combined_times = np.concatenate((audio_peaks, mouse_clicks, visual_changes))
    combined_times.sort()

    final_times = []
    for time in combined_times:
        if all(abs(time - t) >= min_gap for t in final_times):
            final_times.append(time)
        if len(final_times) >= max_clips:
            break

    print(f"✅ [选择关键帧] 选取的时间戳: {final_times}")
    return final_times

# 7. Extract Video Clip
def extract_video_clips(video_path, timestamps, output_folder, clip_duration=10):
    print(f"📌 [提取视频片段] 处理中: {video_path}")
    os.makedirs(output_folder, exist_ok=True)

    for i, timestamp in enumerate(timestamps):
        start_time = max(timestamp - 5, 0)
        output_clip = os.path.join(output_folder, f"clip_{i+1}.webm")
        command = [
            "ffmpeg", "-ss", str(start_time), "-i", video_path, "-t", str(clip_duration),
            "-an",  # no voice
            "-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0",
            "-y", output_clip
        ]
        subprocess.run(command)
        print(f"🎬 [提取视频片段] 片段 {i+1} 完成: {output_clip}")

# 8. Extract Keyframe Screenshot
def extract_screenshots(video_path, timestamps, output_folder):
    print(f"📌 [生成关键帧截图] 开始: {video_path}")
    os.makedirs(output_folder, exist_ok=True)

    for i, timestamp in enumerate(timestamps):
        output_image = os.path.join(output_folder, f"frame_{i+1}.jpg")
        command = [
            "ffmpeg", "-ss", str(timestamp), "-i", video_path,
            "-vframes", "1", "-q:v", "2", "-y", output_image
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"🖼️ [生成关键帧截图] 截图 {i+1} 成功: {output_image}")
        else:
            print(f"❌ [生成关键帧截图] 失败: {result.stderr}")


# main program

# Extract audio
audio_path = "output_audio.wav"
extract_audio(audio_file, audio_path)

# Record mouse clicks
mouse_click_log = "mouse_clicks.csv"
record_mouse_clicks(video_screen, mouse_click_log)

# Extract event time points
audio_peaks = get_audio_peaks(audio_path)
mouse_clicks = get_mouse_click_times(mouse_click_log)
visual_changes = get_visual_change_times(video_screen, save_folder="high_diff_frames")

# Filter keyframe time points
final_key_frames = get_final_key_frames(audio_peaks, mouse_clicks, visual_changes)

# Export Video Clip + Screenshot
if final_key_frames:
    extract_video_clips(video_screen, final_key_frames, "key_frames")
    extract_screenshots(video_screen, final_key_frames, "key_frames")
else:
    print("No valid keyframes, skip video clip and screenshot extraction!")

