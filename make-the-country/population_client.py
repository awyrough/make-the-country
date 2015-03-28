"""
BigQuery Client for Recreating US Census Data, census block by census block.

Alexander Penn Hill Wyrough
3/17/2015

https://github.com/awyrough/make-the-country
"""

# SYSTEM IMPORTS
import logging, os, httplib2
# GOOGLE IMPORTS
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
from googleapiclient.errors import HttpError
# SECRET IMPORTS
from secret import GOOGLE_PRIVATE_KEY_FILE, GOOGLE_DEVELOPER_PROJECT_NUMBER, GOOGLE_SERVICE_EMAIL, GOOGLE_DEVELOPER_PROJECT_ID

from upload_census_data.googlebigqueryclient import GoogleBigQueryClient, loadTable

from output_schema import population_output_schema

# LOGGING DECLARATION
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s %(filename)s: %(message)s",
                    level=logging.WARNING)

class PopulationClient():
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

    def run_query(self, query_str):
        """
        Execute query_str and return results as list of lists.
        """
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
            print(response)
            return []

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

        data_results = []
        while True:
            try:
                results = self.client.jobs().getQueryResults(**getQueryResultsParams).execute()
            except HttpError as e:
                logger.error("[Big Query SQL Query Polling Error]: %s", e)
                return []

            try:
                [data_results.append(row) for row in results["rows"]]
            except KeyError:
                logger.error("[No rows returned]")
                break

            if 'pageToken' in results: getQueryResultsParams["pageToken"] = results["pageToken"]
            else: break

        return data_results

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
        return income_query

    def get_tract_data(self, db_type, county_id, tract_id, state_name):
        """
        Return all rows from DEMO data base of state, corresponding to tract_id and state_id.
        """
        if db_type != "income":
            query_str = self.get_query_string(db_type, state_name, county_id, tract_id)
        else:
            query_str = self.get_income_query(state_name, county_id, tract_id)
        return self.run_query(query_str)

    def get_all_tracts_in_county(self, state, county):
        """
        Return a list of strings for all tracts within the county within the state.

        Note: BigQuery does support DISTINCT, must use GROUP BY
        """
        if county:
            query_str = "SELECT TRACT FROM [%s.%s_demo] WHERE COUNTY IN (\"%s\") GROUP BY TRACT ORDER BY TRACT ASC" % (state, state, county)
        else:
            query_str = "SELECT TRACT FROM [%s.%s_demo] GROUP BY TRACT ORDER BY TRACT ASC" % (state, state)                        
        # Extract only the TRACT ID from the field: value = census tract
        # EX: [{"f": [{"v": "000100"}]}, ... ]
        return [x["f"][0]["v"] for x in self.run_query(query_str)]

    def get_counties_in_state(self, state):
        """
        Return a list of strings for all counties within the state.
        """
        query_str = "SELECT COUNTY FROM [%s.%s_demo] GROUP BY COUNTY ORDER BY COUNTY ASC" % (state, state)
        return [x["f"][0]["v"] for x in self.run_query(query_str)]        

    def get_demo_data(self, state, county, tract):
        """
        Get all Census data for given state, county, and tract. 

        This should return a row for every census block within the tract/county/state combo.
        This should return an identical number of rows for corresponding group/family queries.
        """
        demo = self.get_tract_data("demo", county, tract, state)
        return demo

    def get_group_data(self, state, county, tract):
        """
        Get group data for a given state, county, and tract.

        This should return a row for every census block within the tract/county/state combo.
        This should return an identical number of rows for corresponding demo/family queries.
        """
        group = self.get_tract_data("group", county, tract, state)
        return group

    def get_family_data(self, state, county, tract):
        """
        Get family data for a given state, county, and tract.

        This should return a row for every census block within the tract/county/state combo.
        This should return an identical number of rows for corresponding demo/group queries.
        """
        family = self.get_tract_data("family", county, tract, state)
        return family

    def get_income_data(self, state, county, tract):
        """
        Get income data for a given state, county, and tract.

        This should return 1 row/list of data.
        """
        income = self.get_tract_data("income", county, tract, state)
        return income

    def get_all_tracts(self, state, county):
        """
        Return all tracts within a county.
        """
        tracts = self.get_all_tracts_in_county(state, county)
        return tracts

    def get_all_counties(self, state):
        """
        Return all counties within a state.
        """
        counties = self.get_counties_in_state(state)
        return counties

    def get_population_count(self, state, county):
        """
        Return the population in a given county.
        """
        query_str = "SELECT SUM(POP100) FROM [%s.%s_demo] WHERE COUNTY IN (\"%s\")" % (state, state, county)
        return int(self.run_query(query_str)[0]["f"][0]["v"])

#################################################################################################
"""
Below are standalone methods that do not require the use of a Google BigQuery client.

Cleaner methods that are more simpler, better for one off.

My attempt at overloading.
"""
################################################################################################# 

def get_demo_data(state, county, tract):
    """
    Get all Census data for given state, county, and tract. 

    This should return a row for every census block within the tract/county/state combo.
    This should return an identical number of rows for corresponding group/family queries.
    """
    client = PopulationClient()
    demo = client.get_tract_data("demo", county, tract, state)
    return demo

def get_group_data(state, county, tract):
    """
    Get group data for a given state, county, and tract.

    This should return a row for every census block within the tract/county/state combo.
    This should return an identical number of rows for corresponding demo/family queries.
    """
    client = PopulationClient()
    group = client.get_tract_data("group", county, tract, state)
    return group

def get_family_data(state, county, tract):
    """
    Get family data for a given state, county, and tract.

    This should return a row for every census block within the tract/county/state combo.
    This should return an identical number of rows for corresponding demo/group queries.
    """
    client = PopulationClient()
    family = client.get_tract_data("family", county, tract, state)
    return family

def get_income_data(state, county, tract):
    """
    Get income data for a given state, county, and tract.

    This should return 1 row/list of data.
    """
    client = PopulationClient()
    income = client.get_tract_data("income", county, tract, state)
    return income

def get_all_tracts(state, county):
    """
    Return all tracts within a county.
    """
    client = PopulationClient()
    tracts = client.get_all_tracts_in_county(state, county)
    return tracts

def get_all_counties(state):
    """
    Return all counties within a state.
    """
    client = PopulationClient()
    counties = client.get_counties_in_state(state)
    return counties

def unpack_bigquery_row(data):
    return [x["v"] for x in data["f"]]

def load_population_result(filename):
    """
    Create table in population_output dataset for the name perscibed by filename.
    """
    actual_name = filename.split("/")[2]
    state = filename.split("/")[1]
    gs_location = "gs://population-output/" + state + "/" + actual_name
    dataset = "population_output"
    table = actual_name.split(".")[0]
    client = GoogleBigQueryClient()
    loadTable(client.client, GOOGLE_DEVELOPER_PROJECT_ID, dataset, table, gs_location, population_output_schema)

def main():
    pass
    filename = "population-output/new_jersey/new_jersey_BHETWX_salem.csv"
    load_population_result(filename)

if __name__ == "__main__":
    main()