# Bits and Pieces from Previous Versions
# Copyright (c) 2022 Jonatan Jalle Steller <jonatan.steller@adwmainz.de>
#
# MIT License


# TODO revise this function for a new table feature
def cleanTable( table:list, cleanUps:list ) -> list:
    '''
    Cleans up table data by flattening lists and via search-and-replace patterns

        Parameters:
            table (list): Table-like multidimensional list
            cleanUps (list): List of string pairs to search and replace
        
        Returns:
            list: Cleaned-up table
    '''

    # Go into each individual value in the table
    cleanTable = []
    for tableLine in table:
        cleanTableLine = []
        for value in tableLine:

            # Join lists into cleaned-up strings
            if isinstance( value, list ):
                cleanValue = []
                for valueEntry in value:
                    if not isinstance( valueEntry, str ):
                        cleanValue += str( valueEntry )
                    else:
                        cleanValue += valueEntry
                cleanValue = ';'.join( cleanValue )

            # Turn all other types (apart from strings and lists) into cleaned-up strings
            elif not isinstance( value, str ):
                cleanValue = str( value )
            else:
                cleanValue = value
            
            # Apply each clean-up
            for cleanUp in cleanUps:
                cleanValue = cleanValue.replace( cleanUp[0], cleanUp[1] )

            # Add clean value to new table line
            cleanTableLine += cleanValue

        # Add clean table line to new table
        cleanTable += cleanTableLine
    
    # Return clean table
    return cleanTable


def saveTableAsCsv( header:list, table:list, fileName:str ):
    '''
    Saves a table-like multidimensional list as a comma-separated value file

        Parameters:
            header (list): Simple list containing table header strings
            table (list): Table-like multidimensional list
            fileName (str): Name of the file to save
    '''

    # Open file
    f = open( fileName + '.csv', 'w' )

    # Write headers
    headerString = '"' + '","'.join( header ) + '"\n'
    f.write( headerString )
    f.flush

    # Write table line by line
    for tableLine in table:
        tableString = '"' + '","'.join( tableLine ) + '"\n'
        f.write( tableString )
        f.flush


def compileDataFromJson( resources:list, fields:list, rest:float ) -> list:
    '''
    Grabs data from JSON resources and saves them in a table-like multidimensional list

        Parameters:
            resources (list): All resource URLs to cycle through
            fields (list): All fields to retrieve per resource
            rest (float): Number of seconds to rest in between API calls

        Returns:
            list: Table-like multidimensional list of data
    '''

    # Cycle through all resources
    table = []
    for resource in resources:

        # Open resource and check whether JSON is valid
        try:
            dataRaw = urlopen( resource )
            try:
                data = loads( dataRaw.read() )

                # Add required data to table line
                tableLine = []
                for field in fields:
                    if data.get( field ):
                        tableLine += data.get( field )
                    else:
                        tableLine += False
                
                # Add table line to table
                table += tableLine

            # Note if JSON is not valid or the resource not available
            except:
                print( '- Invalid JSON: ' + resource )
        except:
            print( '- Resource not available: ' + resource )
        
        # Let the server rest
        sleep( rest )

    # Return the resulting table as a multidimensional list
    return table


table = compileDataFromJson( resources, fields, rest )
table = cleanTable( table, cleanUps )
saveTableAsCsv( header, table, 'cvma-metadata' )