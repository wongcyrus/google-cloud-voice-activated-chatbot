sudo apt-get update 
sudo apt-get install -y python3-pip python-dev
sudo apt-get install -y ffmpeg

pip install gradio==3.38.0 --use-deprecated=legacy-resolver
pip install --upgrade google-cloud-speech==2.21.0
pip install torch
pip install google-cloud-aiplatform google-cloud-translate google-cloud-speech
 
#[If you encounter space issue on your VM, create a temp folder(/home/user/tmp) and install torch inside it as shown below]
pip install --cache-dir=/home/user/tmp torch

# gcloud services enable speech.googleapis.com
# gcloud services enable translate.googleapis.com
# gcloud services enable aiplatform.googleapis.com