from population_client import get_all_tracts, get_demo_data, get_group_data, get_family_data, get_income_data
from maker_helpers import confirm_command, confirm_output, display_start, display_stop

def make_the_state(state, county, output=True):
    """
    Recreate the state population as of the 2010 census, where the population is aggregated by census block.

    output, when set to false, will write the data to a GoogleBigQuery data table for download and querying. 
    Default is to create a local CSV file. 
    """
    # Validate Use
    confirm = confirm_execution(state, county, output)
    if not confirm:
        display_stop()
        exit()

    # Get all the tracts for the state/county entity

    # Iterate over all tracts in the state/county

        # Get associated data for the tract
            # income
            # demo
            # group

        # iterate over each census block in the census tract
            # income remains constant
            # chug through demo, group, family

        # get next tract
            # update income data

# def main():
#     make_the_state("new_jersey", None)

# if __name__=="__main__":
#     main()