sudo apt-get update 
sudo apt-get install -y python3-pip python-dev
sudo apt-get install -y ffmpeg
sudo apt-get install gcc libpq-dev build-essential -y
sudo apt-get install python-dev  python-pip -y
sudo apt-get install python3-dev python3-pip python3-venv python3-wheel -y

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# gcloud services enable speech.googleapis.com
# gcloud services enable aiplatform.googleapis.com