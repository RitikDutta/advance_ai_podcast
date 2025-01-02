#!/usr/bin/python

import os
import sys
import time
import random
import httplib2
import http.client as httplib  # Correctly import http.client as httplib

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

# Constants
CLIENT_SECRETS_FILE = "client.json"
OAUTH2_CREDENTIALS_FILE = "youtube_upload_credentials.json"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = f"""
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   {os.path.abspath(CLIENT_SECRETS_FILE)}

with information from the API Console
https://console.cloud.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
"""

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
    httplib.NotConnected,             # Correctly reference httplib exceptions
    httplib.IncompleteRead,
    httplib.ImproperConnectionState,
    httplib.CannotSendRequest,
    httplib.CannotSendHeader,
    httplib.ResponseNotReady,
    httplib.BadStatusLine,
)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


class YouTubeUploader:
    def __init__(
        self,
        client_secrets_file: str = CLIENT_SECRETS_FILE,
        credentials_file: str = OAUTH2_CREDENTIALS_FILE,
    ):
        """
        Initialize the YouTubeUploader with client secrets and credentials file paths.

        :param client_secrets_file: Path to the OAuth 2.0 client secrets JSON file.
        :param credentials_file: Path to the credentials storage file.
        """
        self.client_secrets_file = client_secrets_file
        self.credentials_file = credentials_file
        self.youtube = None

    def authenticate(self):
        """
        Authenticate the user and build the YouTube service object.
        """
        flow = flow_from_clientsecrets(
            self.client_secrets_file,
            scope=YOUTUBE_UPLOAD_SCOPE,
            message=MISSING_CLIENT_SECRETS_MESSAGE,
        )
        storage = Storage(self.credentials_file)
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage)

        self.youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            http=credentials.authorize(httplib2.Http()),
        )

    def upload_video(
        self,
        file_path: str,
        title: str,
        description: str,
        category: str = "22",
        keywords: str = "",
        privacy_status: str = "public",
    ):
        """
        Upload a video to YouTube with the given parameters.

        :param file_path: Path to the video file to upload.
        :param title: Title of the video.
        :param description: Description of the video.
        :param category: Numeric category ID for the video. Default is "22" (People & Blogs).
        :param keywords: Comma-separated keywords for the video. Optional.
        :param privacy_status: Privacy status of the video. Choices: "public", "private", "unlisted".
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        if privacy_status not in VALID_PRIVACY_STATUSES:
            raise ValueError(
                f"Invalid privacy status: {privacy_status}. "
                f"Choose from {VALID_PRIVACY_STATUSES}."
            )

        tags = [tag.strip() for tag in keywords.split(",")] if keywords else None

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category,
            },
            "status": {
                "privacyStatus": privacy_status,
            },
        }

        media_body = MediaFileUpload(file_path, chunksize=-1, resumable=True)

        insert_request = self.youtube.videos().insert(
            part=",".join(body.keys()), body=body, media_body=media_body
        )

        self._resumable_upload(insert_request)

    def _resumable_upload(self, insert_request):
        """
        Handle the resumable upload with retry logic.

        :param insert_request: The request object for inserting the video.
        """
        response = None
        error = None
        retry = 0

        while response is None:
            try:
                print("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if "id" in response:
                        print(f"Video id '{response['id']}' was successfully uploaded.")
                    else:
                        raise Exception(
                            f"The upload failed with an unexpected response: {response}"
                        )
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = f"A retriable error occurred: {e}"

            if error:
                print(error)
                retry += 1
                if retry > MAX_RETRIES:
                    raise Exception("No longer attempting to retry.")

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print(f"Sleeping {sleep_seconds:.2f} seconds and then retrying...")
                time.sleep(sleep_seconds)


                