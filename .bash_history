sudo apt update && sudo apt upgrade -y && sudo apt install -y python3-pip python3-dev ffmpeg
scp -i "D:\table\Data5703\lixiang\usyd-cs14-2.pem" D:\table\Data5703\recording\17.ipynb\* ubuntu@54.252.172.84:~/
ls
python3 --version
sudo apt update
sudo apt install -y python3-pip
pip3 install numpy librosa Pillow imagehash
python3 -m venv venv
source venv/bin/activate
sudo apt update
sudo apt install -y python3.12-venv
python3 -m venv venv
source venv/bin/activate
pip install numpy librosa Pillow imagehash boto3
pip3 install boto3
ls
pip install nbconvert
jupyter nbconvert --to script 17.ipynb
python 17.py
source ~/venv/bin/activate
ls
source ~/venv/bin/activate
aws s3 ls s3://cs14-2-recordingtool/
sudo apt update
sudo apt install awscli -y
aws --version
sudo apt update
sudo apt install awscli -y
source ~/venv/bin/activate
sudo apt update
sudo apt install awscli -y
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo apt install unzip -y
unzip awscliv2.zip
sudo ./aws/install
aws --version
aws configure
source ~/venv/bin/activate
aws configure sso
aws configure
aws s3 ls s3://cs14-2-recordingtool/
source ~/venv/bin/activate
nano process_from_s3.py
source ~/venv/bin/activate
nano process_from_s3.py
source ~/venv/bin/activate
nano process_from_s3.py
source ~/venv/bin/activate
nano process_from_s3.py
source ~/venv/bin/activate
python3 process_from_s3.py
pwd
ls
rm process_from_s3.py.save process_from_s3.py.save.1
ls
rm process_from_s3.py.save.2
ls
nano process_from_s3.py
python3 process_from_s3.py
source ~/venv/bin/activate
ls
cd ~   # 或者你实际保存代码的目录
cd ~ https://github.com/Yuchen528/USYD5703.git
cd ~
git init
git add process_from_s3.py
cat > README.md << 'EOF'
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



