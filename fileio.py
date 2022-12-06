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


# Import libraries
from os import mkdir


def createFolder( folderName:str ):
    '''
    Creates a folder with a given name in the script's directory

        Parameters:
            folderName (str): Name of the folder to create
    '''

    try:
        mkdir( folderName )
    except OSError as error:
        print( '- Using an existing folder (' + folderName + ')' )


def saveAsFile( content:str, fileName:str, fileExtension ):
    '''
    Saves content to a file with a specified name and extension

        Parameters:
            content (str): Content to be saved to file
            fileName (str): Name of the file to create
            fileExtension (str): Extension of the file to create
    '''

    # Write content to file
    f = open( fileName + '.' + fileExtension, 'w' )
    f.write( content )
    f.flush


def saveListAsTxt( list:list, fileName:str ):
    '''
    Saves a one-dimensional list as a text file

        Parameters:
            list (list): Simple one-dimensional list
            fileName (str): Name of the file to save
    '''

    # Open the file
    f = open( fileName + '.txt', 'w' )

    # For each list entry, write a single line
    for listEntry in list:
        f.write( listEntry + '\n' )
        f.flush


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
