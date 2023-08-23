
import os
from pathlib import Path
from flask import escape
import openai

import functions_framework
from google.cloud import datastore

openai.api_type = "azure"
openai.api_base = "https://eastus.api.cognitive.microsoft.com/"
openai.api_version = "2023-06-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")


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
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }

        return ("", 204, headers)
    headers = {"Access-Control-Allow-Origin": "*"}
    
    request_args = request.args

    key = request_args["key"]
    prompt = request_args["prompt"]
    print(f"key: {key}")

    response = openai.Image.create(
        prompt=prompt,
        size='1024x1024',
        n=1
    )
    image_url = response["data"][0]["url"]
              
    return image_url, 200
    
