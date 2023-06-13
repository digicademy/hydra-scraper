# Retrieve files from web sources
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from urllib.request import urlopen

# Import script modules
from helpers.clean import clean_lines


def download_file(url:str) -> dict:
    '''
    Retrieves a file from a URL and returns the content

        Parameters:
            url (str): URL to download the file from

        Returns:
            dict: Provides 'file_type', 'file_extension' and 'content' of the retrieved file
    '''

    # Retrieve URL content
    try:
        response = urlopen(url)

        # Check if response is invalid
        if response.status != 200:
            simple_response = None

        # If response is valid, get clean file content
        else:
            headers = dict(response.headers.items())
            file_type = determine_file_type(headers, False)
            file_extension = determine_file_type(headers, True)
            content = response.read().decode('utf-8')

            # If present, isolate embedded JSON-LD as it is not supported by RDFLib yet
            if determine_file_type(headers, False) == 'rdfa':
                embedded_jsonld = content.find('application/ld+json')
                if embedded_jsonld != -1:
                    embedded_jsonld_start = content.find('>', embedded_jsonld) + 1
                    embedded_jsonld_end = content.find('</script>', embedded_jsonld)
                    if embedded_jsonld_start > 0 and embedded_jsonld_end > embedded_jsonld_start:

                        # Correct previous assumptions
                        file_type = 'json-ld'
                        file_extension = 'jsonld'
                        content = content[embedded_jsonld_start:embedded_jsonld_end]

                        # Remove empty lines
                        content = clean_lines(content)

            # Structure the data
            simple_response = {
                'file_type': file_type,
                'file_extension': file_extension,
                'content': content
            }


    # Notify if URL not available
    except:
        simple_response = None

    # Return simplified response
    return simple_response


def determine_file_type(headers:dict, getFileExtension:bool = False) -> str:
    '''
    Determines the best file type and extension based on the server response

        Parameters:
            headers (dict): Headers of the server response as a dictionary
            getFileExtension (bool, optional): Determines whether the type or the extension is returned
        
        Returns:
            str: Best file extension
    '''

    # Retrieve content type
    content_type = headers['Content-Type']

    # Get best file type and extension, list originally based on
    # https://github.com/RDFLib/rdflib/blob/main/rdflib/parser.py#L237
    # and extended based on further RDFLib documentation
    if 'text/html' in content_type:
        file_type = 'rdfa'
        file_extension = 'html'
    elif 'application/xhtml+xml' in content_type:
        file_type = 'rdfa'
        file_extension = 'xhtml'
    elif 'application/rdf+xml' in content_type:
        file_type = 'xml'
        file_extension = 'xml'
    elif 'text/n3' in content_type:
        file_type = 'n3'
        file_extension = 'n3'
    elif 'text/turtle' in content_type or 'application/x-turtle' in content_type:
        file_type = 'turtle'
        file_extension = 'ttl'
    elif 'application/trig' in content_type:
        file_type = 'trig'
        file_extension = 'trig'
    elif 'application/trix' in content_type:
        file_type = 'trix'
        file_extension = 'trix'
    elif 'application/n-quads' in content_type:
        file_type = 'nquads'
        file_extension = 'nq'
    elif 'application/ld+json' in content_type:
        file_type = 'json-ld'
        file_extension = 'jsonld'
    elif 'application/json' in content_type:
        file_type = 'json-ld'
        file_extension = 'json'
    elif 'application/hex+x-ndjson' in content_type:
        file_type = 'hext'
        file_extension = 'hext'
    elif 'text/plain' in content_type:
        file_type = 'nt'
        file_extension = 'nt'

    # Non-RDF file types that may be useful
    # When you add a file type here, make sure you also list it in the config dictionary
    elif 'application/xml' in content_type:
        file_type = 'lido'
        file_extension = 'xml'
    else:
        raise Exception('Hydra Scraper does not recognise this file type.')

    # Return file extension or type
    if getFileExtension == True:
        return file_extension
    else:
        return file_type
