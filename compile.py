# Compile Data from Web APIs
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
from urllib.request import urlopen
from json import loads
from time import sleep


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
