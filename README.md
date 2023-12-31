
# Google Cloud Voice Activated Chatbot

A Gradio application, Google Cloud Voice Activated Chatbot, enables the user to input Chinese text or Cantonese voice, and utilizes various Google Cloud APIs such as Google Speech to Text, Google Translate, and Vertex AI.

Source referneces:
https://www.googlecloudcommunity.com/gc/Community-Blogs/How-to-quickly-build-a-voice-activated-chatbot-to-interact-with/ba-p/618715 

Enable Google Cloud API
```
gcloud services enable speech.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

GCP application Login 
```
gcloud auth application-default login
gcloud config set project XXXXX
gcloud auth application-default set-quota-project XXXXX
```
Replace XXX with your GCP project name.

Run the server
```
./setup.sh
gradio main.py bot_interface
```

## Deploy to GCP CloudRun

```
gcloud auth login
gcloud config set project XXXXX
gcloud config set run/region asia-east2
gcloud services enable speech.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud run deploy
```

For local test, but it cannot run as no permission.
```
docker build -t chatbot .
docker run -it --rm -p 8000:8000 chatbot
```

