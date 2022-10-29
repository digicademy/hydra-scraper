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
    #'beacon-jsonld',
    #'beacon-rdf',
    #'beacon-ttl',
    #'dump-jsonld',
    #'dump-rdf',
    #'dump-ttl',
    'table-csv'
]

# Configure source URLs
sourcesBase = 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html?tx_cvma_archive[%40widget_0][currentPage]='
#sourcesBase = 'https://corpusvitrearum.de/id/about.html?tx_vocabulary_about%5Bpage%5D='
sourcesIteratorStart = 1
sourcesIteratorEnd = 160

# Rest period for the server in seconds
rest = 0.1

# List all known issues
knownIssues = [
    #'https://corpusvitrearum.de/id/F13073', # Produces an apostrophe issue in the CSV path
    #'https://corpusvitrearum.de/id/F13074', # Produces an apostrophe issue in the CSV path
    #'https://corpusvitrearum.de/id/F13075', # Produces an apostrophe issue in the CSV path
    #'https://corpusvitrearum.de/id/F13076', # Produces an apostrophe issue in the CSV path
    #'https://corpusvitrearum.de/id/F13077', # Produces an apostrophe issue in the CSV path
    #'https://corpusvitrearum.de/id/F13072', # Produces an apostrophe issue in the CSV path
    #'https://corpusvitrearum.de/id/F13071', # Produces an apostrophe issue in the CSV path
    #'https://corpusvitrearum.de/id/F13070', # Produces an apostrophe issue in the CSV path
    #'https://corpusvitrearum.de/id/F13069', # Produces an apostrophe issue in the CSV path
    #'https://corpusvitrearum.de/id/F13068'  # Produces an apostrophe issue in the CSV path
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
if 'beacon-jsonld' in requests or 'beacon-rdf' in requests or 'beacon-turtle' in requests:
    if requestInfo != '':
        requestInfo += requestInfoSeparator
    requestInfo += 'beacon ('

    # Go through individual 'beacon' formats
    if 'beacon-jsonld' in requests:
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

    # Close the string
    requestInfo += requestInfoSubinfo + ')'
    requestInfoSubinfo = ''

# Add 'dump' string if applicable
if 'dump-jsonld' in requests or 'dump-rdf' in requests or 'dump-turtle' in requests:
    if requestInfo != '':
        requestInfo += requestInfoSeparator
    requestInfo += 'dump ('

    # Go through individual 'dump' formats
    if 'dump-jsonld' in requests:
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

# Variables
resources = []
resourceAddition = '/about.'

# Set up the parser
for source in sources:
    html = urlopen( source )
    soup = BeautifulSoup( html, 'html.parser' )

    # Find the right section
    sectionA = soup.find( 'div', {'id': 'content'} )
    sectionB = sectionA.find( 'div', {'class': 'container'} )
    sectionC = sectionB.find( 'div', {'class': 'column-2-3'} )
    sectionD = sectionC.find( 'div' )
    sectionE = sectionD.find( 'div' )
    rows = sectionE.find_all( 'div', {'rel': 'schema:dataFeedElement'} )

    # Alternative path to be activated when the API list is ready
    #sectionOuter = soup.find( 'div', {'id': 'content'} )
    #sectionInner = sectionOuter.find( 'div', {'class': 'container'} )
    #section = sectionInner.find( 'dl' )
    #rows = section.find_all( 'div' )

    # Grab the right string
    for row in rows:
        entry = row.find( 'div' )
        if entry.find( 'div' ):
            entryElement = entry.find( 'div' )
            entryURL = entryElement['resource']
            resources.append( entryURL )

        # Alternative path to be activated when the API list is ready
        #entry = row.find( 'dt' )
        #if entry.find( 'a' ):
            #entryElement = entry.find( 'a' )
            #entryURL = entryElement['href']
            #if entryURL[0] == 'F':
                #resources.append( resourcesBase + entryURL + resourceAddition )

    # Let the server rest
    sleep( rest )

# Remove any known issues from the resources list
for knownIssue in knownIssues:
    if knownIssue in resources:
        resources.remove( knownIssue )


# STEP 5: COMPILE BEACON FILES ################################################

# Go through all 'beacon' requests
for request in requests:
    if request == 'beacon-jsonld' or request == 'beacon-rdf' or request == 'beacon-ttl':

        # Give an update
        print( 'Compiling a beacon file' )

        # Determine requested file extension and create file
        fileExtension = request.replace( 'beacon-', '')
        f = open( 'cvma-beacon-' + fileExtension + '.txt', 'w' )

        # For each resource, write a single line
        for resource in resources:
            f.write( resource + '.' + fileExtension + '\n' )
            f.flush


# STEP 6: COMPILE RESOURCE DUMPS ##############################################

# Go through all 'dump' requests
for request in requests:
    if request == 'dump-jsonld' or request == 'dump-rdf' or request == 'dump-ttl':

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
            fileName = resource.replace( 'https://corpusvitrearum.de/id/', '')
            fileName = 'cvma-dump-' + fileExtension + '/' + fileName

            # And save it to a file
            f = open( fileName + '.' + fileExtension, 'w' )
            f.write( content )
            f.flush

            # Let the server rest
            sleep( rest )


# STEP 7: COMPILE METADATA TABLES #############################################

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


# STEP 8: DONE ################################################################

# Give an update
print( 'Done!' )