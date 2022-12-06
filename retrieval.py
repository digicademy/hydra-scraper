# Retrieve Data from an API
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
from rdflib import Graph

# Import script modules
from fileio import *


def retrieveApiLists( formatParser:str, formatFolder:str, formatUrl:str ) -> list:
    '''
    Retrieves and paginates through API lists, saves them, and returns a beacon list

        Parameters:
            formatParser (str): Name od the parser to use
            formatFolder (str): Name of the folder to save data to
            formatUrl (str): Entry-point URL
        
        Returns:
            list: Beacon list containing item URLs generated from the API calls
    '''

    # Iterator
    listNumber = 1
    listFinalUrl = ''

    # Determine file extension
    fileExtension = 'txt'
    if formatParser == 'json-ld':
        fileExtension = 'json'
    elif formatParser == 'rdf-xml':
        fileExtension = 'rdf'
    elif formatParser == 'turtle':
        fileExtension = 'ttl'

    # Download and save list file
    content = downloadFile( formatUrl )
    saveAsFile( content, formatFolder + '/' + 'list-' + listNumber, fileExtension )

    # Parse the file
    g = Graph().parse( data=content )
    for r in g.triples((None, None, None)):
        print(r)
    # prints: (rdflib.term.URIRef('a:'), rdflib.term.URIRef('p:'), rdflib.term.URIRef('p:'))


    # Get data for beacon and final/next link
    # Repeat
    # Return the beacon list



def downloadFile( url:str ) -> str:
    '''
    Downloads a file from a URL and returns the content

        Parameters:
            url (str): Name of the URL to download the file from
        
        Returns:
            str: Content of the downloaded file
    '''

    # Get the URL's content
    return urlopen( url ).read().decode( 'utf-8' )
