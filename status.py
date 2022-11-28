# File Input and Output
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


def echoRequests( requests:list, formats:list ):
    '''
    Echoes the requests made to the script

        Parameters:
            requests (list): All requests made to the script
            formats (list): All formats to work through
    '''

    # Clean up requests
    requests = [ request.replace( 'beacon and lists', 'beacon and list dump' ) for request in requests ]
    requests = [ request.replace( 'items', 'item dump' ) for request in requests ]
    requests = [ request.replace( 'table', 'data table' ) for request in requests ]

    # Convert formats
    simpleFormats = []
    for format in formats:
        simpleFormats += format[0].upper()

    # Echo string
    print( 'Producing ' + ', '.join( requests ) + 'from' + ', '.join( simpleFormats ) )
