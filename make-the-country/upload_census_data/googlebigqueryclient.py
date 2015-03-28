import logging
import pprint
import json
import os, sys

import httplib2
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
from googleapiclient.errors import HttpError

from secret import GOOGLE_PRIVATE_KEY_FILE, GOOGLE_DEVELOPER_PROJECT_ID, GOOGLE_DEVELOPER_PROJECT_NUMBER, GOOGLE_SERVICE_EMAIL

from census_schema import demo_schema, group_schema, family_schema, income_schema

class GoogleBigQueryClient():
    """
    Google BigQuery API Client for GDELT access and processing.
    """
    def __init__(self):
        """
        Build authorized Google Big Query API Client from project_id and project_number given project google service email.
        """
        SCOPE = 'https://www.googleapis.com/auth/bigquery'
        self.get_private_key()
        credentials = SignedJwtAssertionCredentials(GOOGLE_SERVICE_EMAIL, self.private_key, SCOPE)
        http = httplib2.Http()
        self.http = credentials.authorize(http)
        self.client = build('bigquery', 'v2', http=self.http)
        
    def get_private_key(self):
        """
        Read from *.pem private key file. File path specified in secrets.py.
        """
        BASE = os.path.dirname(os.path.abspath(__file__))
        f = file(os.path.join(BASE, GOOGLE_PRIVATE_KEY_FILE), 'rb')
        self.private_key = f.read()
        f.close()

    def test_access(self):
        """
        Small response test to test authorized client. Working as of 02/25/15.
        """
        datasets = self.client.datasets()
        response = datasets.list(projectId=GOOGLE_DEVELOPER_PROJECT_NUMBER, all="true").execute()
        print(response)
        print('dataset list: \n')
        for d in response['datasets']:
            print("%s\n" % d['id'])

def loadTable(service, projectId, datasetId, targetTableId, sourceCSV, tableSchema, skip=0):
  """
  Load table from Google Cloud Storage into Big Query.
  """
  try:
    jobCollection = service.jobs()
    jobData = {
      'projectId': projectId,
      'configuration': {
          'load': {
            'sourceUris': [sourceCSV],
            'skipLeadingRows': skip,
            'schema': {
              'fields': tableSchema
            },
            'destinationTable': {
              'projectId': projectId,
              'datasetId': datasetId,
              'tableId': targetTableId
            },
          }
        }
      }

    insertResponse = jobCollection.insert(projectId=projectId,
                                         body=jobData).execute()
    import time
    while True:
      job = jobCollection.get(projectId=projectId,
                                 jobId=insertResponse['jobReference']['jobId']).execute()
      print(job)
      if 'DONE' == job['status']['state']:
          print 'Done Loading!'
          return
      print 'Waiting for loading to complete...'
      time.sleep(10)

    if 'errorResult' in job['status']:
      print 'Error loading table: ', pprint.pprint(job)
      return
  except HttpError as err:
    print 'Error in loadTable: ', pprint.pprint(err.resp)


def main():
  client = GoogleBigQueryClient()
  client.test_access()
  # loadTable(client.client, GOOGLE_DEVELOPER_PROJECT_ID, "new_jersey", "new_jersey_demo", "gs://demographic-data/NewJerseyQuery.csv", demo_schema)
  # loadTable(client.client, GOOGLE_DEVELOPER_PROJECT_ID, "new_jersey", "new_jersey_group", "gs://groupquarter-data/NewJerseyGQuery.txt", group_schema)
  # loadTable(client.client, GOOGLE_DEVELOPER_PROJECT_ID, "new_jersey", "new_jersey_family", "gs://family-data/NewJerseyFQuery.txt", family_schema)
  # loadTable(client.client, GOOGLE_DEVELOPER_PROJECT_ID, "new_jersey", "new_jersey_income", "gs://income-data/NewJerseyIncome.csv", income_schema)

if __name__ == "__main__":
    main()