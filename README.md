# AWS S3 Video Processing Script
This project automates the process of downloading `.webm` video and audio recordings from a structured S3 bucket, detecting keyframes, generating video clips and screenshots, and uploading the results back to S3.

##  Features
- Traverse through nested folders in S3 under `recording_results/`
- Download `screen.webm` and `audio.webm`
- Extract keyframes and screenshots
- Upload processed results to `Output/Video Splitting/` in S3
- Automatically creates missing output folders

##  S3 Folder Structure
**Input Example:**
s3://cs14-2-recordingtool/recording_results/
└── 5307ABC/
└── <UUID>/
└── task_1/
├── screen.webm
└── audio.webm
**Output Location:**
s3://cs14-2-recordingtool/Output/Video Splitting/

##  How to Use
1. **Install required libraries**  
   Make sure your virtual environment is activated, then run:

   ```bash
   pip install -r requirements.txt
2.**Run the script
   python process_from_s3.py
3.**AWS credentials
   Ensure your EC2 instance or environment has the appropriate IAM role or .aws/credentials configured.

## Output
Screenshots (PNG)
Extracted video clips (MP4)
Saved in structured S3 output folders


