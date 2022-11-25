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
