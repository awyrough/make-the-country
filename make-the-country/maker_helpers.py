"""
User interaction and printing helpers for make_the_state.py
"""

def confirm_output(state, county, output):
    """
    Confirm where the user wants to put the output.
    """
    pass

def confirm_command(state, county):
    """
    Confirm command of state/county combination
    """
    if not county:
        print("[WARNING]: you are attempting to recreate the entire state of %s. Is this what you want?", state)
        go = raw_input("y/n to continue...")
    else:
        print("[WARNING]: you are attempting to recreate the entire county of %s. Is this what you want? Press Enter.", county)
        go = raw_input("y/n to continue...")
    return (go == "y")

def confirm_execution(state, county, output):
    """
    Return True if the execution should proceed as is, False if not.
    """
    pass

def display_start(state, county, output):
    """
    Display to user what he/she is attempting to do. Begin asking questions.
    """
    pass

def display_stop():
    """
    Display to user that you are stopping the execution.
    """
    pass