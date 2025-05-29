import os
import boto3
import subprocess
import librosa
import numpy as np
import csv
import time
from PIL import Image
import imagehash
from io import BytesIO

s3 = boto3.client("s3")
bucket_name = "cs14-2-recordingtool"
output_prefix = "Output/Video Splitting"

def download_file_from_s3(s3_path, local_path):
    s3.download_file(bucket_name, s3_path, local_path)
    print(f"✅ download: {s3_path} -> {local_path}")

def upload_folder_to_s3(local_folder, s3_folder_prefix):
    for root, _, files in os.walk(local_folder):
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, local_folder)
            s3_key = f"{s3_folder_prefix}/{relative_path}"
            s3.upload_file(local_file_path, bucket_name, s3_key)
            print(f"⬆️ upload: {local_file_path} -> s3://{bucket_name}/{s3_key}")

def extract_audio(video_path, audio_path):
    command = ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def get_audio_peaks(audio_path, sr=22050):
    y, sr = librosa.load(audio_path, sr=sr)
    rms = librosa.feature.rms(y=y)[0]
    peaks = np.where(rms > np.percentile(rms, 90))[0]
    return librosa.frames_to_time(peaks, sr=sr)

def record_mouse_clicks(video_path, csv_path):
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['relative_timestamp'])

def get_mouse_click_times(csv_path):
    if not os.path.exists(csv_path):
        return np.array([])
    with open(csv_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        return np.array([float(row[0]) for row in reader if row])
def get_visual_change_times(video_path, threshold=0.5, frame_rate=1, save_folder="visual_changes"):
    os.makedirs(save_folder, exist_ok=True)
    temp_folder = "temp_frames"
    os.makedirs(temp_folder, exist_ok=True)
    command = [
        "ffmpeg", "-i", video_path, "-vf", f"fps={frame_rate}",
        os.path.join(temp_folder, "frame_%04d.jpg"), "-hide_banner", "-loglevel", "error", "-y"
    ]
    subprocess.run(command)
    timestamps = []
    prev_hash = None
    for i, fname in enumerate(sorted(os.listdir(temp_folder))):
        img_path = os.path.join(temp_folder, fname)
        with Image.open(img_path) as img:
            img_hash = imagehash.phash(img)
        if prev_hash is not None:
            diff = (prev_hash - img_hash) / len(img_hash.hash)**2
            if diff >= threshold:
                timestamps.append(i / frame_rate)
        prev_hash = img_hash
    return np.array(timestamps)

def get_final_key_frames(audio_peaks, mouse_clicks, visual_changes, min_gap=20, max_clips=10):
    combined = np.concatenate((audio_peaks, mouse_clicks, visual_changes))
    combined.sort()
    final = []
    for t in combined:
        if all(abs(t - f) >= min_gap for f in final):
            final.append(t)
        if len(final) >= max_clips:
            break
    return final

def extract_video_clips(video_path, timestamps, output_folder, clip_duration=10):
    os.makedirs(output_folder, exist_ok=True)
    for i, timestamp in enumerate(timestamps):
        start_time = max(timestamp - 5, 0)
        output_clip = os.path.join(output_folder, f"clip_{i+1}.webm")
        command = [
            "ffmpeg", "-ss", str(start_time), "-i", video_path, "-t", str(clip_duration),
            "-an", "-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0",
            "-y", output_clip
        ]
        subprocess.run(command)

def extract_screenshots(video_path, timestamps, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for i, timestamp in enumerate(timestamps):
        output_image = os.path.join(output_folder, f"frame_{i+1}.jpg")
        command = [
            "ffmpeg", "-ss", str(timestamp), "-i", video_path,
            "-vframes", "1", "-q:v", "2", "-y", output_image
        ]
        subprocess.run(command)

def process_all_folders():
    paginator = s3.get_paginator("list_objects_v2")
    response_iterator = paginator.paginate(Bucket=bucket_name, Prefix="recording_results/", Delimiter="/")

    for top_level in response_iterator:
        if "CommonPrefixes" not in top_level:
            continue
        for sub1 in top_level["CommonPrefixes"]:
            prefix1 = sub1["Prefix"]
            response1 = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix1, Delimiter="/")
            for sub2 in response1.get("CommonPrefixes", []):
                prefix2 = sub2["Prefix"]
                task_path = f"{prefix2}task_1/"
                screen_key = task_path + "screen.webm"
                audio_key = task_path + "audio.webm"

                local_screen = "screen.webm"
                local_audio = "audio.webm"
                download_file_from_s3(screen_key, local_screen)
                download_file_from_s3(audio_key, local_audio)

                audio_path = "output_audio.wav"
                extract_audio(local_audio, audio_path)

                record_mouse_clicks(local_screen, "mouse_clicks.csv")

                audio_peaks = get_audio_peaks(audio_path)
                mouse_clicks = get_mouse_click_times("mouse_clicks.csv")
                visual_changes = get_visual_change_times(local_screen)

                final_key_frames = get_final_key_frames(audio_peaks, mouse_clicks, visual_changes)

                if final_key_frames:
                    uuid = prefix2.strip("/").split("/")[-1]
                    output_folder = f"output/{uuid}"
                    extract_video_clips(local_screen, final_key_frames, os.path.join(output_folder, "clips"))
                    extract_screenshots(local_screen, final_key_frames, os.path.join(output_folder, "screenshots"))
                    upload_folder_to_s3(output_folder, f"{output_prefix}/{uuid}")

if __name__ == "__main__":
    process_all_folders()
