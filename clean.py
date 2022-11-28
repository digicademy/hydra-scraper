# Clean Up Data
# Copyright (C) 2022 Jonatan Jalle Steller <jonatan.steller@adwmainz.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


# Import libraries
from validators import url


def cleanRequests( requests:list ) -> list:
    '''
    Cleans up a request list

        Parameters:
            requests (list): List of requests for the script to work through
        
        Returns:
            list: Cleaned-up requests list
    '''

    # Request whitelist
    standardRequests = [
        'beacon and lists',
        'items',
        'table'
    ]

    # Go through requests and add them to a standardised list
    cleanRequests = []
    for standardRequest in standardRequests:
        if standardRequest in requests:
            cleanRequests += standardRequest

    # Return the standardised list
    return cleanRequests


def cleanFormats( formats:list ) -> list:
    '''
    Checks a formats list for the right length and use of a URL

        Parameters:
            formats (list): Multidimensional list of formats for the script to work through
        
        Returns:
            list: Cleaned-up formats list
    '''

    # Parser whitelist
    standardParsers = [
        'json-ld',
        'rfx-xml',
        'turtle'
    ]

    # Only use formats when all values are strings, a valid number of values per entry, a proper parser and a URL
    formatIndex = 0
    for format in formats:
        if all( isinstance( value, str ) for value in format ) \
            or not len( format ) == 3 \
            or format[1] not in standardParsers \
            or not url( format[2] ):
            formats.remove( format )

        # Clean up the folder name
        formatIndex = formatIndex + 1
        cleanFormat = str( format[1] )
        cleanFormat = cleanFormat.replace( '/', '' )
        cleanFormat = cleanFormat.replace( '\\', '' )
        cleanFormat = cleanFormat.replace( ' ', '' )
        formats[ formatIndex ][1] = cleanFormat

    # Return the standardised list
    return formats


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
