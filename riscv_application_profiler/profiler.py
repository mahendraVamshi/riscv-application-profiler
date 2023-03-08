def run(log, output):
    '''
    Parses the given log and generates meaningful information.
    '''
    
    # Open the log file
    with open(log, 'r') as logfile:

        # Read the log file
        lines = logfile.readlines()

    # Print the number of lines in the log file
    print("Number of lines in the log file: ", len(lines))