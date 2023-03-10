def run(log, output):
    '''
    Parses the given log and generates meaningful information.
    '''
    
    # Open the log file
    with open(log, 'r') as logfile:

        # Read the log file
        lines = logfile.readlines()
        
    for line in lines :
        if re.match(pattern,line):
            line_count=line_count+1
            
        else:
        
            print(line,line_count)
    
            

print("total number of lines = ", line_count)

    # Print the number of lines in the log file
    print("Number of lines in the log file: ", len(lines))
