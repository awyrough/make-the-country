import logging
import pprint
import json
import os, sys

import httplib2
from apiclient.http import MediaIoBaseUpload
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
from googleapiclient.errors import HttpError

from secret import GOOGLE_PRIVATE_KEY_FILE, GOOGLE_DEVELOPER_PROJECT_ID, GOOGLE_DEVELOPER_PROJECT_NUMBER, GOOGLE_SERVICE_EMAIL

class GoogleGCSClient():
    """
    Google BigQuery API Client for GDELT access and processing.
    """
    def __init__(self):
        """
        Build authorized Google Big Query API Client from project_id and project_number given project google service email.
        """
        SCOPE = 'https://www.googleapis.com/auth/devstorage.full_control'
        self.get_private_key()
        credentials = SignedJwtAssertionCredentials(GOOGLE_SERVICE_EMAIL, self.private_key, SCOPE)
        http = httplib2.Http()
        self.http = credentials.authorize(http)
        self.client = build('storage', 'v1', http=self.http)
        
    def get_private_key(self):
        """
        Read from *.pem private key file. File path specified in secrets.py.
        """
        BASE = os.path.dirname(os.path.abspath(__file__))
        f = file(os.path.join(BASE, GOOGLE_PRIVATE_KEY_FILE), 'rb')
        self.private_key = f.read()
        f.close()

    def list_buckets(self):
        """
        List all of the buckets in a GCS project.
        """
        buckets_request = self.client.buckets().list(project=GOOGLE_DEVELOPER_PROJECT_ID)
        try:
            response = buckets_request.execute()
        except HttpError as e:
            print("[Error in buckets access for GCS]: error: %s", e)
        else:
            if not "items" in response:
                print("There are no buckets in this project")
            buckets = [bucket["name"] for bucket in response["items"]]
        return buckets

    def list_objects_in_bucket(self, bucket):
        """
        List of all the objects in a GCS bucket and return pertinent information.
        """
        object_request = self.client.objects().list(bucket=bucket)
        try:
            response = object_request.execute()
        except HttpError as e:
            print("[Error in objects access for GCS]: error: %s", e)
        else:
            if not "items" in response:
                print("There are no objects in this project")
            return [
                {
                    "name": obj["name"],
                    "mediaLink": obj["mediaLink"],
                    "selfLink": obj["selfLink"]
                }
            for obj in response["items"]]

    def create_bucket(self, bucket_name):
        """
        Create bucket within a project.
        """
        object_request = self.client.buckets().insert(project=GOOGLE_DEVELOPER_PROJECT_ID, body={"name": bucket_name})
        try:
            object_request.execute()
        except HttpError as e:
            print("[Error in objects access for GCS]: error: %s", e)
        else:
            return True

    def add_object_to_bucket(self, bucket, obj_name, name):
        """
        Upload media object (specified by filename) to bucket and call it name.
        """
        media = MediaIoBaseUpload(open(obj_name, "r"), "text/plain")
        
        # Define body request here (ACL, etc) (Optional)
        body = {

        }

        # Define request here (Necesssary)
        upload_params = {
            "bucket": bucket,
            "name": name,
            "body": body,
            "media_body": media, 
        }

        upload_request = self.client.objects().insert(**upload_params)
        try:
            response = upload_request.execute()
        except HttpError as e:
            print("[Error in objects access for GCS]: error: %s", e)
        else:
            return response


def load_data_to_big_query(filename):
    """
    Upload local results file to Google Cloud Storage.

    Local file path: /population-output/state/filename
    GCS bucket path: /population-output/state/filename
    """
    # load data to GCS cloud store
    upload_client = GoogleGCSClient()
    name = filename.split("/")[1] + "/" + filename.split("/")[2]
    try:
        response = upload_client.add_object_to_bucket("population-output", filename, name)
    except HttpError as e:
        return False
    else:
        return True

def main():
    pass
    # load_data_to_big_query("population-output/new_jersey/new_jersey_1IG3Y8_salem.csv")

if __name__ == "__main__":
    main()