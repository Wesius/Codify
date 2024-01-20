import time
from google.cloud import vision
from openai import OpenAI
def detect_text(image_path):
    """Detects text in the image using Google Cloud Vision API."""

    client = vision.ImageAnnotatorClient()

    with open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )

    return " ".join(text.description for text in texts)


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