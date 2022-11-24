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
