# Simple Scraper for API Data
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
from bs4 import BeautifulSoup
from time import sleep
from os import mkdir

# Import script modules
from config import *
from status import *
from retrieval import *
from compile import *
from clean import *
from fileio import *


# CLEAN AND ECHO SCRIPT CONFIGURATION #########################################


# Clean requests and formats
requests = cleanRequests( requests )
formats = cleanFormats( formats )

# Echo them
echoRequests( requests, formats )


# BEACON AND LISTS ############################################################


# Go through each format
for format in formats:

    # Make central format info available
    formatFolder = format[1]
    formatFolderEcho = formatFolder.upper()

    # Create the folder to use for this format
    if 'beacon and lists' in requests:
        createFolder( format[1] )

        # Cycle through lists
        print( formatFolderEcho + ': Downloading all lists' )
        beacon = retrieveApiLists( format[0], format[1], format[2] )

        # Save item URLs as beacon file
        print( formatFolderEcho + ': Creating a beacon file' )
        saveListAsTxt( beacon, format[1] + '/' + 'beacon' )


# ITEMS #######################################################################
# TABLE #######################################################################


    # TODO Table generation
    if 'beacon and lists' in requests and 'items' in requests and 'table' in requests:
        # Change resources to resource + resourceAddition + 'json'
        print( 'Compiling a metadata table' )
        table = compileDataFromJson( resources, fields, rest )
        table = cleanTable( table, cleanUps )
        saveTableAsCsv( header, table, 'cvma-metadata' )


# FINISH ######################################################################

# All done
print( 'All done!' )









# STEP 4: IDENTIFY ALL RESOURCES ##############################################

# Give an update
print( 'Identifying resource URLs' )

# Variable
resources = []

# Set up the parser
for source in sources:
    html = urlopen( source )
    soup = BeautifulSoup( html, 'html.parser' )

    # Find the right section
    sectionOuter = soup.find( 'div', {'id': 'content'} )
    sectionInner = sectionOuter.find( 'div', {'class': 'container'} )
    section = sectionInner.find( 'dl' )
    rows = section.find_all( 'div' )

    # Grab the right string
    for row in rows:
        entry = row.find( 'dt' )
        if entry.find( 'a' ):
            entryElement = entry.find( 'a' )
            entryURL = entryElement['href']
            if entryURL[0] == 'F':
                resources.append( resourcesBase + entryURL )

    # Let the server rest
    sleep( rest )

# Remove any known issues from the resources list
for knownIssue in knownIssues:
    if knownIssue in resources:
        resources.remove( knownIssue )


# STEP 5: COMPILE BEACON FILES ################################################

# Go through all 'beacon' requests
for request in requests:
    if request == 'beacon-json' or request == 'beacon-rdf' or request == 'beacon-ttl' or request == 'beacon-cgif':

        # Give an update
        print( 'Compiling a beacon file' )

        # Determine requested file extension and create file

        # resource + resourceAddition + fileExtension
        fileExtension = request.replace( 'beacon-', '')
        saveListAsTxt( resources, request )


# STEP 6: COMPILE SOURCE DUMPS ###############################################

# Go through all 'listdump' requests
for request in requests:
    if request == 'listdump-json' or request == 'listdump-rdf' or request == 'listdump-ttl' or request == 'listdump-cgif':

        # Give an update
        print( 'Compiling a list dump' )

        # Determine requested file extension and create folder
        fileExtension = request.replace( 'listdump-', '')
        try:
            mkdir( 'cvma-listdump-' + fileExtension )
        except OSError as error:
            print( '- Using an existing folder' )

        # Compile all lists to download
        lists = [w.replace('html', fileExtension) for w in sources]

        # Download and save each list
        listiterator = 0
        for individuallist in lists:
            listiterator = listiterator + 1

            content = urlopen( individuallist ).read().decode( 'utf-8' )
            fileName = 'list-' + str(listiterator).zfill(3)
            fileName = 'cvma-listdump-' + fileExtension + '/' + fileName

            # And save it to a file
            f = open( fileName + '.' + fileExtension, 'w' )
            f.write( content )
            f.flush

            # Let the server rest
            sleep( rest )


# STEP 7: COMPILE RESOURCE DUMPS ##############################################

# Go through all 'dump' requests
for request in requests:
    if request == 'dump-json' or request == 'dump-rdf' or request == 'dump-ttl' or request == 'dump-cgif':

        # Give an update
        print( 'Compiling a resource dump' )

        # Determine requested file extension and create folder
        fileExtension = request.replace( 'dump-', '')
        try:
            mkdir( 'cvma-dump-' + fileExtension )
        except OSError as error:
            print( '- Using an existing folder' )

        # For each resource, download content
        for resource in resources:
            content = urlopen( resource + resourceAddition + fileExtension ).read().decode( 'utf-8' )
            fileName = resource.replace( resourcesBase, '')
            fileName = 'cvma-dump-' + fileExtension + '/' + fileName

            # And save it to a file
            f = open( fileName + '.' + fileExtension, 'w' )
            f.write( content )
            f.flush

            # Let the server rest
            sleep( rest )