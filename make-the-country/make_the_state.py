from __future__ import division

import sys, argparse, os

from datetime import datetime

from population_client import PopulationClient, unpack_bigquery_row, load_population_result
from maker_helpers import confirm_execution, display_stop, display_start, display_county, display_local_output, display_end

from maker_helpers import fix_state_name, find_county, make_random_file_name
from maker_helpers import output_block

from population_builder import extract_income, build_census_block
from gcs_client import load_data_to_big_query

def make_the_state(state, county, output=True, county_code=None):
    """
    Recreate the state population as of the 2010 census, where the population is aggregated by census block.

    output, when set to false, will write the data to a GoogleBigQuery data table for download and querying. 
    Default is to create a local CSV file. 
    """
    if state != "New Jersey": print("only NJ for now"); display_stop(); exit()
    # Validate Use
    confirm = confirm_execution(state, county, output)
    if not confirm: display_stop(); exit()
    display_start(state, county, output)
    # not ready for output to bigquery
    session = PopulationClient()

    # convert pretty state name to file friendly state name
    internal_state = fix_state_name(state)
    # make the output
    filename = make_random_file_name(internal_state, county)
    display_local_output(filename, output)
    file_open = open(filename, "w+")

    # Get all the tracts for the state/county entity
    if not county_code:
        counties = session.get_all_counties(internal_state)
    else:
        counties = [county_code]

    start = datetime.now()
    print("----------------------------------------------------\n")
    print("started at " + str(datetime.now()) + "\n")
    print("----------------------------------------------------\n")

    # declare id variables
    house_count = 0
    person_count = 0

    for county in counties:
        county_population = display_county(session, internal_state, county)
        tracts = session.get_all_tracts(internal_state, county)
        population_made_county = 0
        previous_log = 100000
        # Iterate over all tracts in the county
        for tract in tracts:
            # Get income data for tract
            income = session.get_income_data(internal_state, county, tract)
            income_data = unpack_bigquery_row(income[0])
            family_income, non_family_income = extract_income(income_data)
            # Collect data for  tract
            demo = session.get_demo_data(internal_state, county, tract)
            group = session.get_group_data(internal_state, county, tract)
            family = session.get_family_data(internal_state, county, tract)
            for i in range(len(demo)):
                demo_row = unpack_bigquery_row(demo[i])
                group_row = unpack_bigquery_row(group[i])
                family_row = unpack_bigquery_row(family[i])
                # BUILD CENSUS BLOCK
                block, house_count, person_count = build_census_block(demo_row, group_row, family_row, 
                                                                        family_income, non_family_income, 
                                                                                house_count, person_count)
                output_block(block, output, fileobj=file_open)
                population_census_block = int(demo_row[6])
                population_made_county+=population_census_block
                # END OF CENSUS BLOCK LOOP
                if (population_made_county > previous_log):
                    log_progress(county_population, population_made_county, start)
                    previous_log += 100000
            
            # END OF TRACT LOOP  

        # END OF COUNTY LOOP
    file_open.close()
    log_progress(county_population, population_made_county, start)
    if not output:
        success = load_data_to_big_query(filename)
        if success == True:
            print("----------------------------------------------------\n")
            print("* Uploading to Google BigQuery:                     \n")
            print("* Here are google status updates...                 \n")
            print("----------------------------------------------------\n")
            load_population_result(filename)
            os.remove(filename)
        else:
            print("There was an error loading the file to GCS: %s", success)

    display_end(state, county, output, filename)


def log_progress(total, processed, start):
    """
    Log progress after each county.
    """
    people_to_go = total - processed
    percent_to_go = (people_to_go / total) * 100.00
    percent_done = 100.00 - percent_to_go
    message = "" \
                "----------------------------------------------------\n" \
                "* PROGRESS REPORT:                                  \n" \
                "* You have this left %0.2f%% to go...               \n" \
                "* You have finished this much %0.2f%% so far...     \n" \
                "* It has taken this long: %s                        \n" \
                "----------------------------------------------------\n" % (percent_to_go, percent_done, str(datetime.now() - start))
    print(message)

def get_make_the_state_input():
    print("[INPUT]: What state are you trying to make?")
    state = raw_input("Type the name of your state...    ")
    print("[INPUT]: Do you want to make the whole state? Or just a country?    ")
    county = raw_input("Type the name of the county (or yes for the whole state)    ")
    print("[INPUT]: Do you want to dump the results locally?    ")
    output = raw_input("y/n to continue...    ")

    if (county == "yes"):
        county = None
        county_code = None
    else:
        county_code = find_county(state, county)
        if not county_code:
            print("ERROR: COUNTY NOT FOUND")
            display_stop()
            exit()
    if output == "n":
        output = False
    else:
        output = True
    make_the_state(state, county, output, county_code)

def main():
    parser = argparse.ArgumentParser(description="Make the state simulations")
    parser.add_argument('--interactive', dest="run", action="store_true", help="run an interactive prompt")
    parser.add_argument('--bigquery-output', dest="output", action="store_false", help="put the output into big query")
    parser.add_argument('--state', metavar="S", dest="state", help="the state")
    parser.add_argument('--county', metavar="C", dest="county", help="the county")

    args = parser.parse_args()
    if not args.run:
        if not args.state:
            print("[ERROR]: you need to provide a valid state")
            display_stop()
        else:
            make_the_state(args.state, args.county, args.output, find_county(args.state, args.county))
    else:
        get_make_the_state_input()


if __name__=="__main__":
    main()