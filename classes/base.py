# Base class to provide reporting capabilities
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from os import linesep
from urllib import request


class HyBase:

    # Vars
    quiet = None
    status = []


    def __init__(self, quiet:bool = False):
        '''
        Base class to provide reporting capabilities

            Parameters:
                quiet (bool): Avoid intermediate progress reports
        '''

        # Assign arguments to object
        self.quiet = quiet


    def echo_note(self, note:str):
        '''
        Show a note to the user

            Parameters:
                note (str): Note to show the user
        '''

        # Echo note or add to final report
        if self.quiet != True:
            print(note)


    def echo_progress(self, note:str, current:int = None, max:int = None):
        '''
        Show progress information to the user

            Parameters:
                note (str): Note to show the user
                current (int): Current number used to calculate a percentage
                max (int): Total number used to calculate a percentage
        '''

        # Start string
        if self.quiet != True:
            echo_string = '- ' + note + '… '

            # Echo string if loop has not started yet
            if current == None and max == None:
                print(echo_string, end='\r')
                
            # Calculate percentage if task is not complete
            elif current < max:
                progress = int((current / max ) * 100)
                echo_string += f"{progress:02}" + '%'
                print(echo_string, end='\r')

            # End line when task is done
            else:
                echo_string += 'done!'
                print(echo_string)


    def __download_file(self, url:str, content_type:str = None) -> dict:
        '''
        Retrieve a file from a URL and return the content

            Parameters:
                url (str): URL to download the file from
                content_type (str): Content type to request

            Returns:
                dict: Provides 'file_type', 'file_extension' and 'content' of the retrieved file
        '''

        # Retrieve URL content
        try:
            if content_type != None:
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
                file_type = self.__determine_file_type(headers, False)
                file_extension = self.__determine_file_type(headers, True)
                content = response.read().decode('utf-8')

                # If present, isolate embedded JSON-LD as it is not supported by RDFLib yet
                if self.__determine_file_type(headers, False) == 'rdfa':
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
                            content = self.__strip_lines(content)

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


    def __local_file(self, file_path:str, content_type:str) -> dict:
        '''
        Retrieve a local file and return the content

            Parameters:
                file_path (str): Path to open the file at
                content_type (str): Content type to parse

            Returns:
                dict: Provides 'file_type', 'file_extension' and 'content' of the retrieved file
        '''

        # Retrieve file content
        try:
            with open(file_path) as f:
                content = f.read()

                # Get file type and file extension
                headers = {
                    'Content-Type': content_type
                }
                file_type = self.__determine_file_type(headers, False)
                file_extension = self.__determine_file_type(headers, True)

                # Structure the data
                simple_response = {
                    'file_type': file_type,
                    'file_extension': file_extension,
                    'content': content
                }

        # Notify if file not available
        except:
            simple_response = None

        # Return simplified response
        return simple_response


    def __determine_file_type(self, headers:dict, get_file_extension:bool = False) -> str:
        '''
        Determine the best file type and extension based on the server response

            Parameters:
                headers (dict): Headers of the server response as a dictionary
                get_file_extension (bool): Determines whether the type or the extension is returned
            
            Returns:
                str: Best file extension
        '''

        # Retrieve content type
        content_type = headers['Content-Type']

        # Get best RDF file type and extension, list originally based on
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

        # Non-RDF file types
        elif 'application/xml' in content_type:
            file_type = 'xml'
            file_extension = 'xml'
        else:
            raise Exception('Hydra Scraper does not recognise this file type.')

        # Return file extension or type
        if get_file_extension == True:
            return file_extension
        else:
            return file_type


    def __save_file(self, content:str, file_path:str):
        '''
        Save content to a file using a full file path

            Parameters:
                content (str): Content to save to file
                file_path (str): Path of file to create
        '''

        # Write content to file
        f = open(file_path, 'w')
        f.write(content)
        f.flush


    def __strip_string(self, input:str) -> str:
        '''
        Takes a string, removes quotation marks and newlines, and returns the string

            Parameters:
                string (str): Input string to clean

            Returns:
                str: Cleaned output string
        '''

        # Remove offending characters
        input = input.replace('"', '\'')
        input = input.replace('\n', '')
        input = input.replace('\r', '')

        # Return clean string
        return input


    def __strip_lines(self, input:str) -> str:
        '''
        Takes a multi-line string, removes empty lines and comments, and returns the string

            Parameters:
                input (str): Input string to remove lines from

            Returns:
                str: Cleaned output string
        '''

        # Split up by lines and remove empty ones or comments
        lines = [
            line for line in input.splitlines()
            if line.strip() and line[0] != '#'
        ]

        # Return re-assembled string
        return linesep.join(lines)
