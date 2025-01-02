"""
Install an additional SDK for JSON schema support Google AI Python SDK

$ pip install google.ai.generativelanguage
"""
from dotenv import load_dotenv
import os
import json

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")


import os
import time
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

genai.configure()

class Generate_title:
  def __init__(self):
    pass

  def upload_to_gemini(self, path, mime_type=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

  def wait_for_files_active(self, files):
    """Waits for the given files to be active.

    Some files uploaded to the Gemini API need to be processed before they can be
    used as prompt inputs. The status can be seen by querying the file's "state"
    field.

    This implementation uses a simple blocking polling loop. Production code
    should probably employ a more sophisticated approach.
    """
    print("Waiting for file processing...")
    for name in (file.name for file in files):
      file = genai.get_file(name)
      while file.state.name == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(10)
        file = genai.get_file(name)
      if file.state.name != "ACTIVE":
        raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()

  def generate_content(self):
    # Create the model
    generation_config = {
      "temperature": 1,
      "top_p": 0.95,
      "top_k": 40,
      "max_output_tokens": 8192,
      "response_schema": content.Schema(
        type = content.Type.OBJECT,
        enum = [],
        required = ["title", "description"],
        properties = {
          "title": content.Schema(
            type = content.Type.STRING,
          ),
          "description": content.Schema(
            type = content.Type.STRING,
          ),
        },
      ),
      "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
      model_name="gemini-2.0-flash-exp",
      generation_config=generation_config,
      system_instruction="i have a transcript file , u have to create a exiting youtube title, title should describe the whole video not a particular topic in the transcript make the title more generalized and creative  make it more like people click on the video , make it  catchy, and a description for the video of that transcript file , make the discription in medium length around 100 words and well formatted , add the thankyou message from my channel and also add hashtags in the last as well",
    )

    # TODO Make these files available on the local file system
    # You may need to update the file paths
    files = [
      self.upload_to_gemini("transcript.txt", mime_type="text/plain"),
    ]

    # Some files have a processing delay. Wait for them to be ready.
    self.wait_for_files_active(files)

    chat_session = model.start_chat(
      history=[
        {
          "role": "user",
          "parts": [
            files[0],
          ],
        },
      ]
    )

    response = chat_session.send_message("INSERT_INPUT_HERE")
    try:
      response_json = json.loads(response.text)
      return response_json.get("title"), response_json.get("description")
    except json.JSONDecodeError as e:
      print(f"Error decoding JSON: {e}")
      print("Raw response text:", response.text)
      return None, None
