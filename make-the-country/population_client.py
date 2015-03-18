import logging
import pprint
import json
import os, sys

import httplib2
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
from googleapiclient.errors import HttpError

from secret import GOOGLE_PRIVATE_KEY_FILE, GOOGLE_DEVELOPER_PROJECT_ID, GOOGLE_DEVELOPER_PROJECT_NUMBER, GOOGLE_SERVICE_EMAIL

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s %(filename)s: %(message)s",
                    level=logging.INFO)

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

    def get_query_string(self, db, state, county, tract):
        """
        Return query string for given database and state. 
        """
        tract_query = "SELECT * FROM [%s.%s_%s] WHERE TRACT IN (\"%s\") AND COUNTY IN (\"%s\")" % (state, state, db, tract, county)
        return tract_query

    def get_income_query(self, state, county, tract):
        """
        Return query string for income database of state.
        """
        income_query = "SELECT * FROM [%s.%s_income] WHERE GEO_id2 LIKE \"%%%s%s\"" % (state, state, county, tract)
        print(income_query)
        return income_query

    def get_tract(self, db_type, county_id, tract_id, state_name):
        """
        Return all rows from DEMO data base of state, corresponding to tract_id and state_id.
        """
        if db_type != "income":
            query_str = self.get_query_string(db_type, state_name, county_id, tract_id)
        else:
            query_str = self.get_income_query(state_name, county_id, tract_id)
        query_body = {'query': query_str}

        # EXECUTE THE QUERY, KICK OFF JOB
        try:
            response = self.client.jobs().query(projectId=GOOGLE_DEVELOPER_PROJECT_NUMBER, body=query_body).execute()
        except HttpError as e:
            logger.error("[BigQuery SQL Error]: %s", e)
            return []

        # GATHER QUERY AND JOB METADATA
        try:
            numRows = response['totalRows']
            jobId = response['jobReference']['jobId'] 
            projectId = response['jobReference']['projectId']
            jobComplete = response['jobComplete']
        except KeyError as e:
            logger.error("[The result didn't return anything]: ERROR: %s", e) 

        # ACCESS THE JOB OF THE QUERY, TO POLL FOR RESULTS
        try:
            job = self.client.jobs().get(projectId=GOOGLE_DEVELOPER_PROJECT_NUMBER, jobId=jobId).execute()
        except HttpError as e:
            logger.error("[BigQuery SQL Execute Job Error]: %s", e)
            return []

        getQueryResultsParams = {
            "projectId": GOOGLE_DEVELOPER_PROJECT_NUMBER,
            "jobId": jobId,
            "maxResults": 1000, #ARBITRARY
        }
        census_results = []
        while True:
            try:
                results = self.client.jobs().getQueryResults(**getQueryResultsParams).execute()
            except HttpError as e:
                logger.error("[Big Query SQL Query Polling Error]: %s", e)
                return []

            try:
                [census_results.append(row) for row in results["rows"]]
            except KeyError:
                logger.error("[No rows returned]")
                break

            if 'pageToken' in results: getQueryResultsParams = results["pageToken"]
            else: break

        return census_results

def get_demo_data(state, county, tract):
    """
    Get all Census data for given state, county, and tract. 

    This should return a row for every census block within the tract/county/state combo.
    This should return an identical number of rows for corresponding group/family queries.
    """
    client = GoogleBigQueryClient()
    demo = client.get_tract("demo", county, tract, state)
    return demo

def get_group_data(state, county, tract):
    """
    Get group data for a given state, county, and tract.

    This should return a row for every census block within the tract/county/state combo.
    This should return an identical number of rows for corresponding demo/family queries.
    """
    client = GoogleBigQueryClient()
    group = client.get_tract("group", county, tract, state)
    return group

def get_family_data(state, county, tract):
    """
    Get family data for a given state, county, and tract.

    This should return a row for every census block within the tract/county/state combo.
    This should return an identical number of rows for corresponding demo/group queries.
    """
    client = GoogleBigQueryClient()
    family = client.get_tract("family", county, tract, state)
    return family

def get_income_data(state, county, tract):
    """
    Get income data for a given state, county, and tract.

    This should return 1 row/list of data.
    """
    client = GoogleBigQueryClient()
    income = client.get_tract("income", county, tract, state)
    return income

def main():
    pass

if __name__=="__main__":
    main()