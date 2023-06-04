# Retrieve files from web sources
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from urllib.request import urlopen


def download_file(url:str) -> dict:
    '''
    Downloads a file from a URL and returns the content

        Parameters:
            url (str): URL to download the file from

        Returns:
            dict: 'file_extension' and 'content' of the downloaded file
    '''

    # Retrieve URL content
    try:
        response = urlopen(url)
        simple_response = {
            'file_extension': determine_file_extension(response),
            'content': response.read().decode('utf-8')
        }

    # Notify if URL not available
    except:
        simple_response = None

    # Return simplified response
    return simple_response


def determine_file_extension(response:object) -> str:
    '''
    Determines the best file extension based on the server response

        Parameters:
            response (object): Server response including headers
        
        Returns:
            str: Best file extension
    '''

    # Retrieve content type
    headers = response.headers.items()
    headers = dict(headers)
    content_type = headers['Content-Type']

    # Get best file extension, list based on
    # https://github.com/RDFLib/rdflib/blob/main/rdflib/parser.py#L237
    if 'text/html' in content_type:
        file_extension = 'htm'
    elif 'application/rdf+xml' in content_type:
        file_extension = 'xml'
    elif 'text/n3' in content_type:
        file_extension = 'n3'
    elif 'text/turtle' in content_type or 'application/x-turtle' in content_type:
        file_extension = 'ttl'
    elif 'application/trig' in content_type:
        file_extension = 'trig'
    elif 'application/trix' in content_type:
        file_extension = 'trix'
    elif 'application/ld+json' in content_type:
        file_extension = 'jsonld'
    elif 'application/json' in content_type:
        file_extension = 'json'
    elif 'text/plain' in content_type:
        file_extension = 'nt'
    else:
        file_extension = 'txt'

    # Return file extension
    return file_extension
