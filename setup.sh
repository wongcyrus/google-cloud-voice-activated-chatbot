sudo apt-get update 
sudo apt-get install -y python3-pip python-dev
sudo apt-get install -y ffmpeg

pip install -r requirements.txt

# gcloud services enable speech.googleapis.com
# gcloud services enable aiplatform.googleapis.com