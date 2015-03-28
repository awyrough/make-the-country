"""
User interaction and printing helpers for make_the_state.py
"""
import json
import string
import random
import csv
from population_client import GoogleBigQueryClient

def confirm_output(state, country, output):
    """
    Confirm where the user wants to put the output.
    """
    message = "" \
                "----------------------------------------------------\n" \
                "* Please confirm where you want me to dump the      \n" \
                "* results of this simulation.                       \n" \
                "* This is very important!!!!!!!!!!!!!!!!!!!         \n" \
                "* You don't want to over write data.                \n" \
                "----------------------------------------------------\n"
    print(message)
    if not output:
        print("[CONFIRM]: you are attempting to place the output of this simulation into GoogleBigQuery")
        print("Is this what you want?")
        go = raw_input("y/n to continue...    ")
    else:
        print("[CONFIRM]: you are attempting to place the output of this simulation into a local CSV file")
        print("Is this what you want?")
        go = raw_input("y/n to continue...    ")        
    return (go == "y")

def confirm_command(state, country):
    """
    Confirm command of state/country combination
    """
    if not country:
        print("[WARNING]: you are attempting to recreate the entire state of %s. Is this what you want?" % state)
        go = raw_input("y/n to continue...    ")
    else:
        print("[WARNING]: you are attempting to recreate the entire country of %s. Is this what you want?" % country)
        go = raw_input("y/n to continue...    ")
    return (go == "y")

def confirm_execution(state, country, output):
    """
    Return True if the execution should proceed as is, False if not.
    """
    command = confirm_command(state, country)
    if not command:
        return False
    destination = confirm_output(state, country, output)
    if not destination:
        return False
    return True

def display_start(state, country, output):
    """
    Display to user what he/she is attempting to do. Begin asking questions.
    """
    message = "" \
                "----------------------------------------------------\n" \
                "* BEGINNING...                                      \n" \
                "* Strap in...here is what is about to happen...     \n" 

    if not country:
        message += "" \
                "----------------------------------------------------\n" \
                "* You are recreating the entire state of %s         \n" \
                "----------------------------------------------------\n" % (state)
    else:
        message += "" \
                "----------------------------------------------------\n" \
                "* You are recreating the country of %s              \n" \
                "* Which is located in the state of %s               \n" % (country, state)

    if not output:
        message += "" \
                "----------------------------------------------------\n" \
                "* The output of this simulation will be located in  \n" \
                "* a GoogleBigQuery Table, I will tell you the name  \n" \
                "* when we are finished.                             \n" \
                "----------------------------------------------------\n"
    else:
        message += "" \
                "----------------------------------------------------\n" \
                "* The output of this simulation will be located in  \n" \
                "* a local CSV file, I will tell you where it is when\n" \
                "* we are finished.                                  \n" \
                "----------------------------------------------------\n" 

    message += "" \
                "----------------------------------------------------\n" \
                "* Sit back, and I will log progress reports         \n" \
                "----------------------------------------------------\n"

    print(message)

def display_stop():
    """
    Display to user that you are stopping the execution.
    """
    message = "" \
                "----------------------------------------------------\n" \
                "* ABORTING...                                       \n" \
                "* No damage done!                                   \n" \
                "* Make the changes, and try again :)                \n" \
                "----------------------------------------------------\n"
    print(message)

def display_county(session, state, county):
    """
    Display to user that you are beginning work on county
    """
    county_pop = session.get_population_count(state, county)
    message = "" \
                "----------------------------------------------------\n" \
                "* Beginning work on county: %s                      \n" \
                "* There are %d residents in the state.              \n" \
                "----------------------------------------------------\n" % (county, county_pop)
    print(message)
    return county_pop

def find_county(state, county):
    """
    Return county FIPS code for given county name in state.
    """
    state_county_file = open(("county_dictionaries/%s.json" % fix_state_name(state)), "r")
    state_county_dict = json.load(state_county_file)
    try:
        return state_county_dict["counties"][county]
    except KeyError:
        return None

def fix_state_name(state):
    """
    Convert "State Name" to "state_name"
    Convert "State to state"
    """
    return "_".join(state.lower().split(" "))

def make_random_file_name(state, county, size=6, chars=string.ascii_uppercase + string.digits):
    """
    Make and return random file name for output.
    "output/state + RANDOM STRING + COUNTY
    """
    file_str = "population-output/" + state + "/" + state + "_" + ''.join(random.choice(chars) for _ in range(size))
    if county:
        file_str += ("_" + "_".join(county.lower().split(" ")))
    return file_str + ".csv"

def display_local_output(filename, output):
    """
    Tell user where the local output will be
    """
    message = "" \
                "----------------------------------------------------\n" \
                "* OUTPUT                                            \n" \
                "* The results will be located in the State folder   \n" \
                "* in the population-output directory                \n" \
                "* The filename is %s                                \n"

    bigquery_message = "" \
                "* We are sending this data to GoogleBigQuery.       \n" \
                "* It will be stored temporarily locally, but will   \n" \
                "* destroyed.                                        \n" \
                "----------------------------------------------------\n"
    
    local_message = "" \
                "* I will remind you at the end...                   \n" \
                "----------------------------------------------------\n"

    if output:
        message+=local_message
    else:
        message+=bigquery_message
    print(message % (filename)) 

def output_block(block, output=True, fileobj=None, db_table=None):
    """
    Write output
    """
    open_file = csv.writer(fileobj, delimiter=",")
    for b in block:
        open_file.writerow(b)