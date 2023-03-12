def run(log, output):
    '''
    Parses the given log and generates meaningful information.
    '''
    
    # Open the log file
    with open(log, 'r') as logfile:
        # Read the log file
        lines = logfile.readlines()

    pattern="^core\s+\d+:\s+\d*\s+(0x[0-9a-fA-F]+)\s+\((0x[0-9a-fA-F]+)\)\s*(x[0-9]*)?(c[0-9]+[_a-z]*)?(mem)?\s*(0x[0-9a-fA-F]*)?\s*(x[0-9]*)?(c[0-9]+[_a-z]*)?(mem)?\s*(0x[0-9a-fA-F]*)?\s*(x[0-9]*)?(c[0-9]+[_a-z]*)?(mem)?\s*(0x[0-9a-fA-F]*)?"

    output_lines=15 #Matched lines that we want to see as a test case
    line_count=0 #Count of matched lines

    
    #reading each line    
    for line in lines :
        # Used for printing the test matches
        if output_lines:
            output_lines=output_lines-1 
            matches=re.findall(pattern,line) #Finding matches       
            print(matches) #printing the matches


        #Used for seeing all matches and counting them along with printing the mismatched lines
        if re.match(pattern,line):
            line_count=line_count+1 #Increasing the count for every match
            
        else:
            print("the line: %s and it's line munber:%d is not matched" %(line, line_count))
        
    
            

print("total matched number of lines = ", line_count)

    # Print the number of lines in the log file
    print("Number of lines in the log file: ", len(lines))
