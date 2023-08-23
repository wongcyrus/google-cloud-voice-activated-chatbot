
import os
from pathlib import Path

import requests
from flask import escape
import openai

import functions_framework
from google.cloud import storage

import smtplib
from email.mime.text import MIMEText
import urllib.parse



openai.api_type = "azure"
openai.api_base = "https://eastus.api.cognitive.microsoft.com/"
openai.api_version = "2023-06-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")

IMAGE_BUCKET = os.getenv("IMAGE_BUCKET")

@functions_framework.http
def genimage(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """

    # Set CORS headers for the preflight request
    if request.method == "OPTIONS":
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, PUT",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }

        return ("", 204, headers)
    headers = {"Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods":"POST, GET, PUT",
            "Access-Control-Allow-Headers": "Content-Type"}

    request_args = request.args

    key = request_args["key"]
    prompt = request_args["prompt"]
    email = request_args["email"]
    print(f"email: {email}")

    if key != os.getenv("SECRET_KEY"):
        return ("Unauthorized", 401, headers)

    response = openai.Image.create(
        prompt=prompt,
        size='1024x1024',
        n=1
    )
    image_url = response["data"][0]["url"]

    image_path =download_image(image_url)
    public_url = upload_image_to_bucket(image_path)

    params = {'key':key, 'email': email, 'public_url': public_url}
    approval_url = os.getenv("APPROVAL_URL")+"?" + urllib.parse.urlencode(params, doseq=True)

    body= f"""
Please check the following image and click the link to approve it.

{public_url}

Approve: 

{approval_url}


"""

    approver_emails = os.getenv("APPROVER_EMAILS").split(",")
    subject = "Verify Gen Image for "+ email
    sender = os.getenv("GMAIL")
    recipients = approver_emails
    password = os.getenv("APP_PASSWORD")

    send_email(subject, body, sender, recipients, password)
                  
    return "Please wait for a moment!", 200
    
def download_image(image_url):   
    # Download image from url
    r = requests.get(image_url, allow_redirects=True)
    # Image name with hash or image_url
    image_name = "image-"+str(hash(image_url))+ ".png"
    image_path = f"/tmp/{image_name}"
    open(image_path, "wb").write(r.content)
    return image_path

def upload_image_to_bucket(image_path):
    # Upload image to bucket
    client = storage.Client()
    bucket = client.get_bucket(IMAGE_BUCKET)
    # extract image name from path
    image_name = Path(image_path).name
    blob = bucket.blob(image_name)
    blob.upload_from_filename(image_path)
    return blob.public_url
    
def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")
