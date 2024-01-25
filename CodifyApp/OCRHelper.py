import time
import base64
import httpx
import json
from decouple import config
from openai import OpenAI

def detect_text(image_path):
    """Detects text in the image using Google Cloud Vision API REST endpoint."""

    # Use your actual Google Cloud Vision API key
    api_key = config('GOOGLE_API_KEY')
    url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'
    headers = {
        'Content-Type': 'application/json'
    }

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('UTF-8')

    # Construct the request body
    request_body = {
        "requests": [
            {
                "image": {
                    "content": encoded_image
                },
                "features": [
                    {
                        "type": "TEXT_DETECTION"
                    }
                ]
            }
        ]
    }

    # Send the request using httpx
    with httpx.Client() as client:
        response = client.post(url, headers=headers, data=json.dumps(request_body))

    # Parse and return the response
    if response.status_code == 200:
        texts = response.json().get('responses', [{}])[0].get('textAnnotations', [])
        return " ".join(text['description'] for text in texts)
    else:
        # Handle errors
        error_message = response.json().get('error', {}).get('message', 'Unknown error')
        raise Exception(f"Error in text detection API: {error_message}")



def generate_java_code(text_prompt, openai_api_key, assistant_id):
    """Generates Java code from the text prompt using OpenAI API."""
    openai = OpenAI(api_key=openai_api_key)


    def create_thread(prompt):
        assistant = openai.beta.assistants.retrieve(assistant_id)
        thread = openai.beta.threads.create()
        message = openai.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=prompt
        )
        run = openai.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)
        return run.id, thread.id

    def check_status(run_id, thread_id):
        run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        return run.status

    my_run_id, my_thread_id = create_thread(text_prompt)

    while check_status(my_run_id, my_thread_id) != "completed":
        time.sleep(2)

    response = openai.beta.threads.messages.list(thread_id=my_thread_id)
    return response.data[0].content[0].text.value if response.data else ""


def process_image_to_java(image, openai_api_key, assistant_id):
    """Processes an image to generate Java code, combining text detection and code generation."""

    text = detect_text(image)
    return generate_java_code(text, openai_api_key, assistant_id)