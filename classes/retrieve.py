# Class to retrieve, morph, and save data
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from os import linesep
from urllib import request

# Import script modules


class HydraRetrieve:

    # Variables
    something = None


    def __init__(self, command, output, report, morph):
        '''
        Retrieve, morph, and save data

            Parameters:
                command (str): ???
                output (str): ???
                report (str): ???
                morph (str): ???
        '''

        # Assign variables
        self.something = something


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a string
        return self.something


    def _strip_string(self, content:str) -> str:
        '''
        Takes a string, removes quotation marks, removes newlines, and returns the string

            Parameters:
                content (str): input string to clean

            Returns:
                str: cleaned output string
        '''

        # Remove offending characters
        content = content.replace('"', '\'')
        content = content.replace('\n', '')
        content = content.replace('\r', '')

        # Return clean string
        return content


    def _strip_lines(self, content:str) -> str:
        '''
        Takes a string, removes empty lines, removes comments, and returns the string

            Parameters:
                content (str): Input string to clean

            Returns:
                str: Cleaned output string
        '''

        # Split up by lines and remove empty ones or comments
        content_lines = [
            line for line in content.splitlines()
            if line.strip() and line[0] != '#'
        ]

        # Return re-assembled string
        return linesep.join(content_lines)


    def download_file(self, url:str, content_type:str = '') -> dict:
        '''
        Retrieves a file from a URL and returns the content

            Parameters:
                url (str): URL to download the file from
                content_type (str): content type to request, defaults to none

            Returns:
                dict: Provides 'file_type', 'file_extension' and 'content' of the retrieved file
        '''

        # Retrieve URL content
        try:
            if content_type != '':
                request_header = { 'Accept': content_type }
                request_object = request.Request(url, headers = request_header)
                response = request.urlopen(request_object)
            else:
                response = request.urlopen(url)

            # Check if response is invalid
            if response.status != 200:
                simple_response = None

            # If response is valid, get clean file content
            else:
                headers = dict(response.headers.items())
                file_type = self._determine_file_type(headers, False)
                file_extension = self._determine_file_type(headers, True)
                content = response.read().decode('utf-8')

                # If present, isolate embedded JSON-LD as it is not supported by RDFLib yet
                if self._determine_file_type(headers, False) == 'rdfa':
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
                            content = output._strip_lines(content)

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


    def save_file(self, content:str, file_path:str):
        '''
        Saves content to a file with a specified name and extension

            Parameters:
                content (str): Content to be saved to file
                file_path (str): Path of the file to create
        '''

        # Write content to file
        f = open(file_path, 'w')
        f.write(content)
        f.flush