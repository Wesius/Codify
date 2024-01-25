import os
from decouple import config
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from CodifyApp.OCRHelper import process_image_to_java

def index(request):
    context = {}

    if request.method == "POST":
        if "image" in request.FILES:
            image_file = request.FILES["image"]

            # Save the image using default_storage
            file_name = default_storage.save(image_file.name, image_file)
            image_path = os.path.join(settings.MEDIA_ROOT, image_file.name)

            # Process the image using the OCR function
            java_code = process_image_to_java(
                image_path,
                # Retrieve OpenAI API key from .env file
                openai_api_key=config('OPENAI_API_KEY'),
                assistant_id="asst_sAipVyYZrnVwhvyoEUavB8BI"
            )
            return render(request, "index.html", {"java_code": java_code})
    else:
        return render(request, "index.html", context)
