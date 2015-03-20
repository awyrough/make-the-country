import sys, argparse

from population_client import get_all_tracts, get_demo_data, get_group_data, get_family_data, get_income_data
from maker_helpers import confirm_execution, display_stop, display_start
from maker_helpers import fix_state_name

def make_the_state(state, county, output=True):
    """
    Recreate the state population as of the 2010 census, where the population is aggregated by census block.

    output, when set to false, will write the data to a GoogleBigQuery data table for download and querying. 
    Default is to create a local CSV file. 
    """
    # Validate Use
    confirm = confirm_execution(state, county, output)
    if not confirm: display_stop(); exit()
    display_start(state, county, output)

    internal_state = fix_state_name(state)

    # Get all the tracts for the state/county entity
    tracts = get_all_tracts(internal_state, county)

    # need a way to iterate through countties when whole state is specified

    next = True
    # Iterate over all tracts in the state/county
    for tract in tracts:
        # Get associated data for the tract
        income = get_income_data(internal_state, county, tract)
        demo = get_demo_data(internal_state, county, tract)
        group = get_group_data(internal_state, county, tract)
        family = get_group_data(internal_state, county, tract)
        for i, x in enumerate(len(demo)):
            row_demo = demo[i]
            row_group = group[i]
            row_family = family[i]
            print(row_demo)
            print(row_group)
            print(row_family)


def get_make_the_state_input():
    print("[INPUT]: What state are you trying to make?")
    state = raw_input("Type the name of your state (lower cased, underscored)...    ")
    print("[INPUT]: Do you want to make the whole state? Or just a country?    ")
    county = raw_input("Type the name of the county (or yes for the whole state)    ")
    print("[INPUT]: Do you want to dump the results locally?    ")
    output = raw_input("y/n to continue...    ")

    if (county == "yes"):
        county = None
    if output == "n":
        output = False
    else:
        output = True
    make_the_state(state, county, output)

def main():
    parser = argparse.ArgumentParser(description="Make the state simulations")
    parser.add_argument('--interactive', metavar='I', dest="run", type=bool, default=False, help="a flag for interactive process")
    parser.add_argument('--state', metavar="S", dest="state", type=str, help="the state")
    parser.add_argument('--county', metavar="C", dest="county", type=str, help="the county")
    parser.add_argument('--output', metavar="O", dest="output", type=bool, default=True, help="the output")

    args = parser.parse_args()

    if args.run:
        if not args.state:
            print("[ERROR]: you need to provide a valid state")
            display_stop()
        else:
            make_the_state(args.state, args.county, args.output)
    else:
        get_make_the_state_input()


if __name__=="__main__":
    main()