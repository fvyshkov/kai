import os
from pathlib import Path

import googleapiclient.errors
#import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.transport.requests import AuthorizedSession

scopes = ['https://www.googleapis.com/auth/photoslibrary.appendonly']

creds = None

if os.path.exists('_secrets_/token_append.json'):
    creds = Credentials.from_authorized_user_file('_secrets_/token_append.json', scopes)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            '_secrets_/client_secret.json', scopes)
        creds = flow.run_local_server()
    print(creds)
    # Save the credentials for the next run
    with open('_secrets_/token_append.json', 'w') as token:
        token.write(creds.to_json())


authed_session = AuthorizedSession(creds)


def upload_photo(file_path):
    upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
    headers = {
        'Content-Type': 'application/octet-stream',
        'X-Goog-Upload-File-Name': file_path.name,
        'X-Goog-Upload-Protocol': 'raw',
    }

    with open(file_path, 'rb') as photo:
        photo_bytes = photo.read()

    response = authed_session.post(upload_url, data=photo_bytes, headers=headers)

    if response.status_code == 200:
        return response.text  # This is the uploadToken needed for the next step
    else:
        print(f"Failed to upload photo. Status code: {response.status_code}, Response: {response.text}")
        return None



def add_photo_to_album(upload_token, album_id=None):
    url = 'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate'
    body = {
        'newMediaItems': [{
            'simpleMediaItem': {
                'uploadToken': upload_token
            }
        }]
    }

    if album_id:
        body['albumId'] = album_id

    response = authed_session.post(url, json=body)

    if response.status_code == 200:
        print("Photo added to album successfully.")
    else:
        print(f"Failed to add photo to album. Status code: {response.status_code}, Response: {response.text}")



def upload_file(filename):
    # read image from file
    with open(filename, "rb") as f:
        image_contents = f.read()

    # upload photo and get upload token
    response = authed_session.post(
        "https://photoslibrary.googleapis.com/v1/uploads",
        headers={},
        data=image_contents)
    upload_token = response.text

    response = authed_session.post(
            'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate',
            headers = { 'content-type': 'application/json' },
            json={
                "newMediaItems": [{
                    "description": "Test photo",
                    "simpleMediaItem": {
                        "uploadToken": upload_token,
                        "fileName": "test.jpg"
                    }
                }]
            }
    )
    print(response.text)


def create_album_with_authed_session(album_name):
    url = 'https://photoslibrary.googleapis.com/v1/albums'
    body = {
        'album': {'title': album_name}
    }

    response = authed_session.post(url, json=body)

    if response.status_code == 200:
        print(f"Album created successfully. Response: {response.json()}")
    else:
        print(f"Failed to create album. Status code: {response.status_code}, Response: {response.text}")
    return response.json()['id']


def find_last_file(directory):
    # List all files in the directory
    files = [os.path.join(directory, f) for f in os.listdir(directory) if
             os.path.isfile(os.path.join(directory, f))]

    # Find the file with the latest modification time
    if not files:
        return None  # No files in directory
    latest_file = max(files, key=os.path.getmtime)
    return latest_file
"""
album_id = create_album_with_authed_session("test_album")

file_path = Path("/Users/fvyshkov/Downloads/cropped_.jpg")

# Upload photo
upload_token = upload_photo(file_path)
if upload_token:
    # Add photo to album
    add_photo_to_album(upload_token, album_id)
"""