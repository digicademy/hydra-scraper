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

# CONFIGURATION

request = [
    'csv'
    #'dump-jsonld',
    #'dump-rdf',
    #'dump-ttl',
    #'beacon-jsonld',
    #'beacon-rdf',
    #'beacon-ttl',
]
sourcesBase = 'https://corpusvitrearum.de/cvma-digital/bildarchiv.html?tx_cvma_archive[%40widget_0][currentPage]='
#sourcesBase = 'https://corpusvitrearum.de/id/about.html?tx_vocabulary_about%5Bpage%5D='
sourcesIteratorStart = 1
sourcesIteratorEnd = 160
knownIssues = [
    #'https://corpusvitrearum.de/id/F13073', # Apostrophe issue in CSV path
    #'https://corpusvitrearum.de/id/F13074', # Apostrophe issue in CSV path
    #'https://corpusvitrearum.de/id/F13075', # Apostrophe issue in CSV path
    #'https://corpusvitrearum.de/id/F13076', # Apostrophe issue in CSV path
    #'https://corpusvitrearum.de/id/F13077', # Apostrophe issue in CSV path
    #'https://corpusvitrearum.de/id/F13072', # Apostrophe issue in CSV path
    #'https://corpusvitrearum.de/id/F13071', # Apostrophe issue in CSV path
    #'https://corpusvitrearum.de/id/F13070', # Apostrophe issue in CSV path
    #'https://corpusvitrearum.de/id/F13069', # Apostrophe issue in CSV path
    #'https://corpusvitrearum.de/id/F13068' # Apostrophe issue in CSV path
]


# STEP 1: IMPORT LIBRARIES

from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
from json import loads
from os import mkdir


# STEP 2: DETERMINE REQUEST TYPE

if 'csv' in request:
    print( 'Request: all metadata as comma-separated values' )
elif 'dump-jsonld' in request:
    print( 'Request: dump of all JSON-LD files' )
elif 'dump-rdf' in request:
    print( 'Request: dump of all RDF files' )
elif 'dump-ttl' in request:
    print( 'Request: dump of all TTL (Turtle) files' )
elif 'beacon-jsonld' in request:
    print( 'Request: beacon file with all JSON-LD URLs' )
elif 'beacon-rdf' in request:
    print( 'Request: beacon file with all RDF URLs' )
elif 'beacon-ttl' in request:
    print( 'Request: beacon file with all TTL (Turtle) URLs' )


# STEP 3: LIST ALL SOURCES

# Give an update
print( 'Identifying source URLs' )

# Variable
sources = []

# Compile all source URLs
for sourcesIterator in range( sourcesIteratorStart, sourcesIteratorEnd + 1 ):
    sources.append( sourcesBase + str( sourcesIterator ) )


# STEP 4: LIST ALL RESOURCES

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
        #entry = row.find( 'dt' )
        #if entry.find( 'a' ):
            #entryElement = entry.find( 'a' )
            #entryURL = entryElement['href']
            #if entryURL[0] == 'F':
                #resources.append( resourcesBase + entryURL + resourceAddition )


    # Let the server rest
    sleep(0.2)

# Remove known issues
for knownIssue in knownIssues:
    if knownIssue in resources:
        resources.remove( knownIssue )


# STEP 5A: GATHER DATA FROM RESOURCES

# Check path
if 'csv' in request:

    # Give an update
    print( 'Gathering data from resources' )

    # Open file and write headers
    f = open( 'cvma-metadata.csv', 'w' )
    header = '"ID","Title","State","City","Building","Location ID","Location Latitude","Location Longitude","Date Beginning","Date End","Iconclasses"\n'
    f.write( header )
    f.flush

    # Get and parse resource content
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

            # Save the output to the file
            f.write( output )
            f.flush

        # Make a note if JSON is not valid
        except ValueError as e:
            print( '- Invalid: ' + resource )

        # Let the server rest
        sleep(0.2)


# STEP 5B: DOWNLOAD RESOURCES

# Check path
if 'dump-jsonld' in request or 'dump-rdf' in request or 'dump-ttl' in request:

    # Give an update
    print( 'Downloading resources' )

    # Define file ending
    for currentRequest in request:
        fileExtension = currentRequest.replace( 'dump-', '')

    # Create folder
    try:
        mkdir( 'cvma-dump-' + fileExtension )
    except OSError as error:
        print( '- Skipping folder creation' )
        

    # Write one line per resource
    for resource in resources:
        content = urlopen( resource + resourceAddition + fileExtension ).read().decode( 'utf-8' )
        fileName = resource.replace( 'https://corpusvitrearum.de/id/', '')
        fileName = 'cvma-dump-' + fileExtension + '/' + fileName

        # Save content to file
        f = open( fileName + '.' + fileExtension, 'w' )
        f.write( content )
        f.flush


# STEP 5C: COMPILE RESOURCE URLS

# Check path
if 'beacon-jsonld' in request or 'beacon-rdf' in request or 'beacon-ttl' in request:

    # Give an update
    print( 'Compiling resource URLs' )

    # Define file ending
    for currentRequest in request:
        fileExtension = currentRequest.replace( 'beacon-', '')

    # Open file
    f = open( 'cvma-beacon-' + fileExtension + '.txt', 'w' )

    # Write one line per resource
    for resource in resources:
        f.write( resource + '.' + fileExtension + '\n' )
        f.flush


# STEP 6: DONE

# Give an update
print( 'Done!' )