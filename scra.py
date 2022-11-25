# Scraper for CVMA Web Data
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

# CONFIGURATION ###############################################################

# List all requests
requests = [
    'beacon-json',
    'beacon-rdf',
    'beacon-ttl',
    'beacon-cgif',
    'listdump-json',
    'listdump-rdf',
    'listdump-ttl',
    'listdump-cgif',
    'dump-json',
    'dump-rdf',
    'dump-ttl',
    'dump-cgif',
    'table-csv'
]

# Configure URLs
#sourcesBase = 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html?tx_cvma_archive[%40widget_0][currentPage]='
sourcesBase = 'https://corpusvitrearum.de/id/about.html?tx_vocabulary_about%5Bpage%5D='
sourcesIteratorStart = 1
sourcesIteratorEnd = 101
resourcesBase = 'https://corpusvitrearum.de/id/'
resourceAddition = '/about.'

# Rest period for the server in seconds
rest = 0.1

# List all known issues
knownIssues = [
    #'https://corpusvitrearum.de/id/F13073'
]


# STEP 1: IMPORT LIBRARIES ####################################################

from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
from json import loads
from os import mkdir


# STEP 2: DETERMINE REQUEST TYPE ##############################################

# Variables
requestInfo = ''
requestInfoSubinfo = ''
requestInfoSeparator = ', '
requestInfoBeginning = 'Requested: '

# Add 'beacon' string if applicable
if 'beacon-json' in requests or 'beacon-rdf' in requests or 'beacon-ttl' in requests or 'beacon-cgif' in requests:
    if requestInfo != '':
        requestInfo += requestInfoSeparator
    requestInfo += 'beacon ('

    # Go through individual 'beacon' formats
    if 'beacon-json' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'JSON-LD'
    if 'beacon-rdf' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'RDF'
    if 'beacon-ttl' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'TTL'
    if 'beacon-cgif' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'CGIF'

    # Close the string
    requestInfo += requestInfoSubinfo + ')'
    requestInfoSubinfo = ''

# Add 'listdump' string if applicable
if 'listdump-json' in requests or 'listdump-rdf' in requests or 'listdump-ttl' in requests or 'listdump-cgif' in requests:
    if requestInfo != '':
        requestInfo += requestInfoSeparator
    requestInfo += 'list dump ('

    # Go through individual 'dump' formats
    if 'listdump-json' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'JSON-LD'
    if 'listdump-rdf' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'RDF'
    if 'listdump-ttl' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'TTL'
    if 'listdump-cgif' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'CGIF'

    # Close the string
    requestInfo += requestInfoSubinfo + ')'
    requestInfoSubinfo = ''

# Add 'dump' string if applicable
if 'dump-json' in requests or 'dump-rdf' in requests or 'dump-ttl' in requests or 'dump-cgif' in requests:
    if requestInfo != '':
        requestInfo += requestInfoSeparator
    requestInfo += 'dump ('

    # Go through individual 'dump' formats
    if 'dump-json' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'JSON-LD'
    if 'dump-rdf' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'RDF'
    if 'dump-ttl' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'TTL'
    if 'dump-cgif' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'CGIF'

    # Close the string
    requestInfo += requestInfoSubinfo + ')'
    requestInfoSubinfo = ''

# Add 'table' string if applicable
if 'table-csv' in requests:
    if requestInfo != '':
        requestInfo += requestInfoSeparator
    requestInfo += 'table ('

    # Go through individual 'table' formats
    if 'table-csv' in requests:
        if requestInfoSubinfo != '':
            requestInfoSubinfo += requestInfoSeparator
        requestInfoSubinfo += 'CSV'

    # Close the string
    requestInfo += requestInfoSubinfo + ')'
    requestInfoSubinfo = ''

# Output the info string
print( requestInfoBeginning + requestInfo )


# STEP 3: IDENTIFY ALL SOURCES ################################################

# Give an update
print( 'Identifying source URLs' )

# Variable
sources = []

# Compile all source URLs by adding the right number to the base
for sourcesIterator in range( sourcesIteratorStart, sourcesIteratorEnd + 1 ):
    sources.append( sourcesBase + str( sourcesIterator ) )


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
        fileExtension = request.replace( 'beacon-', '')
        f = open( 'cvma-beacon-' + fileExtension + '.txt', 'w' )

        # For each resource, write a single line
        for resource in resources:
            f.write( resource + resourceAddition + fileExtension + '\n' )
            f.flush


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


# STEP 8: COMPILE METADATA TABLES #############################################

# Go through all 'table' requests
for request in requests:
    if request == 'table-csv':

        # Give an update
        print( 'Compiling a metadata table' )

        # Open file and write headers
        f = open( 'cvma-metadata.csv', 'w' )
        header = '"ID","Title","State","City","Building","Location ID","Location Latitude","Location Longitude","Date Beginning","Date End","Iconclasses"\n'
        f.write( header )
        f.flush

        # For each resource, download the JSON content
        for resource in resources:
            output = ''
            dataRaw = urlopen( resource + resourceAddition + 'json' )

            # Check whether JSON is valid
            try:
                data = loads( dataRaw.read() )

                # Add required data to output
                if data.get('@id'):
                    output += '"' + data.get( '@id' ) + '",'
                else:
                    output += '"",'
                if data.get('dc:Title'):
                    output += '"' + data.get( 'dc:Title' ) + '",'
                else:
                    output += '"",'
                if data.get('Iptc4xmpExt:ProvinceState'):
                    output += '"' + data.get( 'Iptc4xmpExt:ProvinceState' ) + '",'
                else:
                    output += '"",'
                if data.get('Iptc4xmpExt:City'):
                    output += '"' + data.get( 'Iptc4xmpExt:City' ) + '",'
                else:
                    output += '"",'
                if data.get('Iptc4xmpExt:Sublocation'):
                    output += '"' + data.get( 'Iptc4xmpExt:Sublocation' ) + '",'
                else:
                    output += '"",'
                if data.get('Iptc4xmpExt:LocationId'):
                    output += '"' + data.get( 'Iptc4xmpExt:LocationId' ) + '",'
                else:
                    output += '"",'
                if data.get('exif:GPSLatitude'):
                    output += '"' + data.get( 'exif:GPSLatitude' ) + '",'
                else:
                    output += '"",'
                if data.get('exif:GPSLongitude'):
                    output += '"' + data.get( 'exif:GPSLongitude' ) + '",'
                else:
                    output += '"",'
                if data.get('cvma:AgeDeterminationStart'):
                    output += '"' + data.get( 'cvma:AgeDeterminationStart' ) + '",'
                else:
                    output += '"",'
                if data.get('cvma:AgeDeterminationEnd'):
                    output += '"' + data.get( 'cvma:AgeDeterminationEnd' ) + '",'
                else:
                    output += '"",'

                # Add iconclasses
                removeIconclass = 'http://iconclass.org/'
                if data.get( 'cvma:IconclassNotation' ):
                    dataIconclasses = data.get( 'cvma:IconclassNotation' )
                    outputIconclasses = ''
                    for dataIconclass in dataIconclasses:
                        outputIconclass = dataIconclass.replace( removeIconclass, '' )
                        if outputIconclasses == '':
                            outputIconclassesSeparator = ''
                        else:
                            outputIconclassesSeparator = ';'
                        outputIconclasses += outputIconclassesSeparator + outputIconclass
                    output += '"' + outputIconclasses + '"\n'
                else:
                    output += '""\n'

                # Save output to file
                f.write( output )
                f.flush

            # Make a note if JSON is not valid
            except ValueError as e:
                print( '- Invalid: ' + resource )

            # Let the server rest
            sleep( rest )


# STEP 9: DONE ################################################################

# Give an update
print( 'Done!' )