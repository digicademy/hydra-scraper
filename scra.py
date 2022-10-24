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

request = 'csv' # csv, dump-jsonld, dump-rdf, dump-ttl, dump-cgif, beacon-jsonld, beacon-rdf, beacon-ttl, beacon-cgif
sourcesBase = 'https://corpusvitrearum.de/id/about.html?tx_vocabulary_about%5Bpage%5D='
sourcesIteratorStart = 1
sourcesIteratorEnd = 155
knownIssues = [ 'https://corpusvitrearum.de/id/F5877/about.' ]


# STEP 1: IMPORT LIBRARIES

from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
from json import loads


# STEP 2: DETERMINE REQUEST TYPE

if request == 'csv':
    print( 'Request: all metadata as comma-separated values' )
elif request == 'dump-jsonld':
    print( 'Request: dump of all JSON-LD files' )
elif request == 'dump-rdf':
    print( 'Request: dump of all RDF files' )
elif request == 'dump-ttl':
    print( 'Request: dump of all TTL (Turtle) files' )
elif request == 'dump-cgif':
    print( 'Request: dump of all CGIF (Culture Graph Interchange Format) files' )
elif request == 'beacon-jsonld':
    print( 'Request: beacon file with all JSON-LD URLs' )
elif request == 'beacon-rdf':
    print( 'Request: beacon file with all RDF URLs' )
elif request == 'beacon-ttl':
    print( 'Request: beacon file with all TTL (Turtle) URLs' )
elif request == 'beacon-cgif':
    print( 'Request: beacon file with all CGIF (Culture Graph Interchange Format) URLs' )


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
resourcesBase = 'https://corpusvitrearum.de/id/'
resourceAddition = '/about.'
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
            entryID = entryElement['href']
            if entryID[0] == 'F':
                resources.append( resourcesBase + entryID + resourceAddition )

    # Let the server rest
    sleep(0.2)

# Remove known issues
for knownIssue in knownIssues:
    resources.remove( knownIssue )


# STEP 5A: GATHER DATA FROM RESOURCES

# Check path
if request == 'csv':

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

        dataRaw = urlopen( resource + 'json' )

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
if request == 'dump-jsonld' or request == 'dump-rdf' or request == 'dump-ttl' or request == 'dump-cgif':

    # Give an update
    print( 'Downloading resources' )

    # Define file ending
    fileExtension = request.replace( 'dump-', '')

    # Write one line per resource
    for resource in resources:
        content = urlopen( resource + fileExtension )
        fileName = resource.replace( 'https://corpusvitrearum.de/id/', '')
        fileName = 'cvma-dump-' + fileExtension + '/' + fileName.replace( '/about', '')
        fileName = fileName + fileExtension

        # Save content to file
        f = open( fileName + fileExtension, 'w' )
        f.write( content )
        f.flush


# STEP 5C: COMPILE RESOURCE URLS

# Check path
if request == 'beacon-jsonld' or request == 'beacon-rdf' or request == 'beacon-ttl' or request == 'beacon-cgif':

    # Give an update
    print( 'Compiling resource URLs' )

    # Define file ending
    fileExtension = request.replace( 'beacon-', '')

    # Open file
    f = open( 'cvma-beacon-' + fileExtension + '.txt', 'w' )

    # Write one line per resource
    for resource in resources:
        f.write( resource + fileExtension + '\n' )
        f.flush


# STEP 6: DONE

# Give an update
print( 'Done!' )